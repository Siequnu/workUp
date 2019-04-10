from flask import render_template, request, send_file, redirect, url_for, send_from_directory, flash, abort, current_app
from random import randint
import os, datetime, json

# SQL
from flask_login import current_user
from app.models import Turma, Upload, Comment, Assignment, Download, User
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
			turmaId = User.get_user_turma_from_user_id (current_user.id)
			if (turmaId == False):
				flash('You do not appear to be part of a class. Please contact your tutor for assistance.')
				return render_template('index.html')
			
			assignmentUploadProgressBarPercentage = app.assignments.models.getAssignmentUploadProgressPercentage ()
			peerReviewProgressBarPercentage = app.assignments.models.getPeerReviewProgressPercentage()
			
			return render_template('index.html', numberOfUploads = numberOfUploads, assignmentUploadProgressBarPercentage = assignmentUploadProgressBarPercentage, peerReviewProgressBarPercentage = peerReviewProgressBarPercentage)
	
	return render_template('index.html')






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
