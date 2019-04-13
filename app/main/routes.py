from flask import render_template, request, send_file, redirect, url_for, send_from_directory, flash, abort, current_app
from random import randint
import os, datetime, json

from flask_login import current_user, login_required
from app.models import Turma, Upload, Comment, Assignment, Download, User
from app import db

db.create_all()
db.session.commit()

from app.main import bp
import app.assignments.models


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
			number_of_uploads = app.files.models.getUploadCountFromCurrentUserId()
			# Display help message if a student has signed up and is not part of a class
			if User.get_user_turma_from_user_id (current_user.id) is None:
				flash('You do not appear to be part of a class. Please contact your tutor for assistance.')
				return render_template('index.html')
			
			assignment_upload_progress_bar_percentage = app.assignments.models.get_assignment_upload_progress_bar_percentage ()
			peer_review_progress_bar_percentage = app.assignments.models.get_peer_review_progress_bar_percentage()
			
			return render_template('index.html', numberOfUploads = number_of_uploads, assignmentUploadProgressBarPercentage = assignment_upload_progress_bar_percentage, peerReviewProgressBarPercentage = peer_review_progress_bar_percentage)
	
	return render_template('index.html')
