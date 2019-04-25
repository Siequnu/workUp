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
			# Display help message if a student has signed up and is not part of a class
			if User.get_user_turma_from_user_id (current_user.id) is None:
				flash('You do not appear to be part of a class. Please contact your tutor for assistance.')
				return render_template('index.html')
			
			number_of_uploads = app.files.models.get_uploaded_file_count_from_user_id(current_user.id)
			number_of_peer_reviews_on_own_uploads = app.assignments.models.get_received_peer_review_count (current_user.id)
			last_upload_humanized_timestamp = app.assignments.models.last_uploaded_assignment_timestamp (current_user.id)
			last_received_peer_review_humanized_timestamp = app.assignments.models.last_incoming_peer_review_timestamp (current_user.id)
			upload_progress_percentage = app.assignments.models.get_assignment_upload_progress_bar_percentage (current_user.id)
			peer_review_progress_percentage = app.assignments.models.get_peer_review_progress_bar_percentage(current_user.id)
			assignments_info = app.assignments.models.get_user_assignment_info (current_user.id)
			return render_template('index.html', number_of_uploads = number_of_uploads, upload_progress_percentage = upload_progress_percentage,
								   peer_review_progress_percentage = peer_review_progress_percentage,
								   number_of_peer_reviews_on_own_uploads = number_of_peer_reviews_on_own_uploads,
								   last_upload_humanized_timestamp = last_upload_humanized_timestamp,
								   last_received_peer_review_humanized_timestamp = last_received_peer_review_humanized_timestamp,
								   assignments_info = assignments_info)
	
	return render_template('index.html')
