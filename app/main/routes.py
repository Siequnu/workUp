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

	

# Choose a random file from uploads folder and send it out for download
@bp.route('/downloadPeerFile/<assignmentId>', methods=['POST'])
@login_required
def downloadRandomFile(assignmentId):
	# Check if user has any previous downloads with pending peer reviews
	pendingAssignments = Comment.getPendingStatusFromUserIdAndAssignmentId (current_user.id, assignmentId)
	if len(pendingAssignments) > 0:
		# User has a pending assignment, send them the same file as before
		alreadyDownloadedAndPendingReviewFileId = pendingAssignments[0][1]
		flash('You have a peer review that you have not yet completed. You have redownloaded the same file.')
		# Get filename of the upload from Id
		conditions = []
		conditions.append(str('id="' + str(alreadyDownloadedAndPendingReviewFileId) + '"'))
		filenameToDownload = app.models.selectFromDb(['filename'], 'upload', conditions)		
		filePath = os.path.join (current_app.config['UPLOAD_FOLDER'], filenameToDownload[0][0])
		# Send SQL data to database
		download = Download(filename=filenameToDownload[0][0], user_id = current_user.id)
		db.session.add(download)
		db.session.commit()
		
		return send_file(filePath, as_attachment=True)
	
	# Make sure not to give the same file to the same peer reviewer twice
	# Get list of files the user has already submitted reviews for
	conditions = []
	conditions.append (str('assignment_id="' + str(assignmentId) + '"'))
	conditions.append (str('user_id="' + str(current_user.id) + '"'))
	completedCommentsIdsAndFileId = app.models.selectFromDb(['id', 'fileid'], 'comment', conditions)
	
	if completedCommentsIdsAndFileId == []:
		filesNotFromUser = Upload.getPossibleDownloadsNotFromUserForThisAssignment (current_user.id, assignmentId)
		
	else:
		# Get an array of filenames not belonging to current user
		previousDownloadFileId = completedCommentsIdsAndFileId[0][1]
		filesNotFromUser = Upload.getPossibleDownloadsNotFromUserForThisAssignment (current_user.id, assignmentId, previousDownloadFileId)
	
	numberOfFiles = len(filesNotFromUser)
	if numberOfFiles == 0:
		flash('There are no files currently available for download. Please check back soon.')
		return redirect(url_for('main.viewAssignments'))
	randomNumber = (randint(0,(numberOfFiles-1)))
	filename = filesNotFromUser[randomNumber]
	randomFile = os.path.join (current_app.config['UPLOAD_FOLDER'], filename)
	
	# Send SQL data to database
	download = Download(filename=filename, user_id = current_user.id)
	db.session.add(download)
	db.session.commit()
	
	# Update comments table with pending commment
	conditions = []
	conditions.append (str('filename="' + str(filename) + '"'))
	uploadId = app.models.selectFromDb(['id'], 'upload', conditions)
	commentPending = Comment(user_id = int(current_user.id), fileid = int(uploadId[0][0]), pending = True, assignment_id=assignmentId)
	db.session.add(commentPending)
	db.session.commit()

	return send_file(randomFile, as_attachment=True)


# Main entrance to the app
@bp.route('/', methods=['GET', 'POST'])
@bp.route('/index', methods=['GET', 'POST'])
def index():
	if current_user.is_authenticated:
		if current_user.username in current_app.config['ADMIN_USERS']:		
			return render_template('index.html', admin = True)
		
		if current_user.username not in current_app.config['ADMIN_USERS']:
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


# View peer review comments
@bp.route("/comments/<fileId>")
@login_required
def viewComments(fileId):
	# Make sure that only the AUTHOR can check comments on their file!
	userId = app.models.selectFromDb(['user_id'], 'upload', [''.join(('id=', str(fileId)))])
	if userId != []: # The upload exists	
		if userId[0][0] == current_user.id:
			# Get assignment ID from upload ID
			assignmentId = app.models.selectFromDb(['assignment_id'], 'upload', [''.join(('id=', str(fileId)))])
			
			# Get comment Ids associated with this upload
			conditions = []
			conditions.append(''.join(('assignment_id=', str(assignmentId[0][0]))))
			conditions.append(''.join(('fileid=', str(fileId))))
			conditions.append('pending=0')
			commentIds = app.models.selectFromDb(['id'], 'comment', conditions)
			cleanCommentIds = []
			for row in commentIds:
				for id in row:
					cleanCommentIds.append(id)
					
			# Get assignment original filename
			upload = app.models.selectFromDb(['original_filename'], 'upload', [''.join(('id=', str(fileId)))])
			uploadTitle = upload[0][0]
			
			return render_template('assignments/comments.html', cleanCommentIds = cleanCommentIds, uploadTitle = uploadTitle)
	abort (403)

# View created assignments status
@bp.route("/viewassignments")
@login_required
def viewAssignments():
	if current_user.username in current_app.config['ADMIN_USERS']:
		# Get admin view with all assignments
		cleanAssignmentsArray = app.assignments.models.getAllAssignments()
		return render_template('assignments/viewassignments.html', assignmentsArray = cleanAssignmentsArray, admin = True)
	elif current_user.is_authenticated:
		# Get user class
		turmaId = app.assignments.models.getUserTurmaFromId(current_user.id)
		if (turmaId == False):
			flash('You are not part of any class and can not see any assignments. Ask your tutor for help to join a class.')
			return render_template('assignments/viewassignments.html') # User isn't part of any class - display no assignments
		else:
			# Get assignments for this user
			cleanAssignmentsArray = app.assignments.models.getUserAssignmentInformation (current_user.id)
			return render_template('assignments/viewassignments.html', assignmentsArray = cleanAssignmentsArray)
	abort (403)
	
	

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
		return redirect(url_for('main.viewAssignments'))
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
	if current_user.is_authenticated and current_user.username in current_app.config['ADMIN_USERS']:	
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

# Admin page to view classes
@bp.route("/peerReviewFormAdmin")
@login_required
def peerReviewFormAdmin():
	if current_user.is_authenticated:
		if current_user.username in current_app.config['ADMIN_USERS']:
			classesArray = app.models.selectFromDb(['*'], 'turma')
			return render_template('admin/classAdmin.html', title='Class admin', classesArray = classesArray)
	abort (403)
