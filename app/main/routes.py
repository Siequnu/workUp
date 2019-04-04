from flask import render_template, request, send_file, redirect, url_for, send_from_directory, flash, abort, current_app
from random import randint
import os, datetime, json

# SQL
from flask_login import current_user
from app.models import Turma, Upload, Comment, Assignment, Download
from app import db

db.create_all()
db.session.commit()

# Blueprint
from app.main import bp

# Login
from flask_login import login_required

# Forms
from app.main.forms import FormModel
from app.forms_peer_review import *

# Models
import app.assignments.models

from wtforms import StringField, BooleanField, SubmitField, RadioField, FormField, TextAreaField
from wtforms.validators import DataRequired

@bp.before_request
def before_request():
	if current_user.is_authenticated:
		current_user.last_seen = datetime.datetime.now()
		db.session.commit()




# Lab
@bp.route('/lab', methods=['GET', 'POST'])
def lab():
	return render_template('lab.html')


# Main entrance to the app
@bp.route('/', methods=['GET', 'POST'])
@bp.route('/index', methods=['GET', 'POST'])
def index():
	if current_user.is_authenticated:
		if app.models.is_admin(current_user.username):
			return render_template('index.html', admin = True)
		else:
			# Get number of uploads
			numberOfUploads = app.files.models.getUploadCountFromCurrentUserId()
			# Get total assignments assigned to user's class
			turmaId = app.assignments.models.getUserTurmaFromId (current_user.id)
			if (turmaId == False):
				flash('You do not appear to be part of a class. Please contact your tutor for assistance.')
				return render_template('index.html')
			
			assignmentUploadProgressBarPercentage = app.assignments.models.getAssignmentUploadProgressPercentage ()
			peerReviewProgressBarPercentage = app.assignments.models.getPeerReviewProgressPercentage()
			
			return render_template('index.html', numberOfUploads = numberOfUploads, assignmentUploadProgressBarPercentage = assignmentUploadProgressBarPercentage, peerReviewProgressBarPercentage = peerReviewProgressBarPercentage)
	
	return render_template('index.html')


# Display an empty review feedback form
@bp.route("/assignments/peerreviewform/<assignmentId>", methods=['GET', 'POST'])
@bp.route("/assignments/peerreviewform", methods=['GET', 'POST'])
@login_required
def createPeerReview(assignmentId = False):
	# Get the appropriate peer review form for the assignment via assignment ID
	if assignmentId:
		peerReviewForm = Assignment.getPeerReviewFormFromAssignmentId(assignmentId)
		peerReviewFormName = peerReviewForm[0][0]	
		form = eval(peerReviewFormName)()
	
	if form.validate_on_submit():
		# Serialise the form contents
		formFields = {}
		for fieldTitle, fieldContents in form.data.items():
			formFields[fieldTitle] = fieldContents
		# Clean the csrf_token and submit fields
		del formFields['csrf_token']
		del formFields['submit']
		formContents = json.dumps(formFields)
		
		# Check if user has any previous downloads with pending peer reviews
		pendingAssignments = Comment.getPendingStatusFromUserIdAndAssignmentId (current_user.id, assignmentId)
		if len(pendingAssignments) > 0:
			# User has a pending peer review - update the empty comment field with the contents of this form and remove pending status
			pendingCommentId = pendingAssignments[0][0]
			updateComment = Comment.updatePendingCommentWithComment(pendingCommentId, formContents)
		
		# The database is now updated with the comment - check the total completed comments
		completedComments = Comment.getCountCompleteCommentsFromUserIdAndAssignmentId (current_user.id, assignmentId)
		if completedComments[0][0] == 1:
			# This is the first peer review, submit
			flash('Peer review 1 submitted succesfully!')
		elif completedComments[0][0] == 2:
			# This is the second peer review, submit
			flash('Peer review 2 submitted succesfully!')
		return redirect(url_for('assignments.view_assignments'))
	return render_template('assignments/peerreviewform.html', title='Submit a peer review', form=form)


# View a completed and populated peer review form
# This accepts both the user's own peer reviews, and other users' reviews
@bp.route("/viewPeerReviewFromAssignment/<assignmentId>/<peerReviewNumber>", methods=['GET', 'POST'])
@bp.route("/viewPeerComment/<commentId>", methods=['GET', 'POST'])
@login_required
def viewPeerReview(assignmentId = False, peerReviewNumber = False, commentId = False):
	if commentId:
		# Check if this peer review is intended for the user trying to view it
		# What file was it made for
		fileId = app.models.selectFromDb(['fileid'], 'comment', [str('id="' + str(commentId) + '"')])
		# Who owns that file
		owner = app.models.selectFromDb(['user_id'], 'upload', [str('id="' + str(fileId[0][0]) + '"')])
		# Is it the same person trying to view this comment?
		if current_user.id is not owner[0][0]:
			abort (403)
		
		# Get assignment ID from comment ID
		assignmentId = app.models.selectFromDb(['assignment_id'],'comment',[(str('id="'+str(commentId)+'"'))])
		# Get the form from the assignmentId
		peerReviewFormName = app.models.selectFromDb(['peer_review_form'],'assignment',[(str('id="'+str(assignmentId[0][0])+'"'))])
		
		# Get the comment content from ID
		comment = app.models.selectFromDb(['comment'],'comment',[(str('id="'+str(commentId)+'"'))])
		unpackedComments = json.loads(comment[0][0])
	else:
		# Get the form from the assignmentId	
		peerReviewFormName = app.models.selectFromDb(['peer_review_form'],'assignment',[(str('id="'+str(assignmentId)+'"'))])
		# Get the first or second peer review - these will be in created order in the DB
		conditions = []
		conditions.append (str('assignment_id="' + str(assignmentId) + '"'))
		conditions.append (str('user_id="' + str(current_user.id) + '"'))
		comments = app.models.selectFromDb(['comment'],'comment',conditions)
		if int(peerReviewNumber) == 1:
			unpackedComments = json.loads(comments[0][0])
		elif int(peerReviewNumber) == 2:
			unpackedComments = json.loads(comments[1][0])
		flash('You can not edit this peer review as it has already been submitted.')
	
	# Import the form class
	formClass = getattr(app.forms_peer_review, str(peerReviewFormName[0][0]))
	# Populate the form
	form = formClass(**unpackedComments)
	# Delete submit button
	del form.submit
	
	return render_template('assignments/peerreviewform.html', title='View a peer review', form=form)


# Admin page to create new peer review form
@bp.route("/addPeerReviewForm", methods=['GET', 'POST'])
@login_required
def addPeerReviewForm():
	if current_user.is_authenticated and app.models.is_admin(current_user.username):
		# If first form is completed, dynamically generate second form
		if request.form:
			# Remove csrf_token, submit fields to leave only the completed boxes
			formDict = request.form.to_dict()
			del formDict['csrf_token']
			del formDict['submit']
			# Sort dictionary by keys
			sortedDict = json.dumps(formDict, sort_keys=True)
			# Dynamically generate new form for title/label information
			for questionNumber, fieldName in sortedDict:
				if fieldName == 'TextAreaField':
					setattr(FormModel, questionNumber, TextAreaField(label=name, validators=[DataRequired()]))
				elif fieldName == 'BooleanField':
					setattr(FormModel, questionNumber, TextAreaField(label=name, validators=[DataRequired()]))
				elif fieldName == 'StringField':
					setattr(FormModel, questionNumber, TextAreaField(label=name, validators=[DataRequired()]))
				elif fieldName == 'RadioField':
					setattr(FormModel, questionNumber, TextAreaField(label=name, validators=[DataRequired()]))
				FormModel.submit = SubmitField('Next step')
				form = FormModel()
			
		else:
			# Generate dynamic field names
			numberOfFields = 10
			i = 1
			names = []
			while i < numberOfFields:
				names.append('Question ' + str(i))
				i = i+1
			questionTypes = [('StringField', 'StringField'), ('BooleanField', 'BooleanField'), ('RadioField', 'RadioField'), ('TextAreaField', 'TextAreaField')]
			for name in names:
				setattr(FormModel, name, RadioField(label=name, choices=questionTypes))
			FormModel.submit = SubmitField('Next step')
			form = FormModel()
		
		return render_template('addPeerReviewForm.html', title='Create new peer review form', form=form)
	abort(403)

# Admin page to view classes
@bp.route("/peerReviewFormAdmin")
@login_required
def peerReviewFormAdmin():
	if current_user.is_authenticated and app.models.is_admin(current_user.username):
			classesArray = app.models.selectFromDb(['*'], 'turma')
			return render_template('admin/classAdmin.html', title='Class admin', classesArray = classesArray)
	abort (403)
