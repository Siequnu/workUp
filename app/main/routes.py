from flask import render_template, flash, current_app, session, request, redirect, url_for, abort
from flask_login import current_user, login_required

import datetime

from app.models import Assignment, Enrollment, ClassLibraryFile, Assignment
import app.assignments.models
import app.files.models
from app import db
from app.main import bp
import app.user

@current_app.before_request
def before_request():
	if current_user.is_authenticated:
		if app.files.models.new_library_files_since_last_seen():
			flash ('New library files have been uploaded', 'info')
		current_user.last_seen = datetime.datetime.now()
		db.session.commit()

# Main entrance to the app
@bp.route('/')
@bp.route('/index')
def index():
	if current_user.is_authenticated:
		greeting = app.main.models.get_greeting ()
		if app.models.is_admin(current_user.username):
			return render_template(
				'index.html', admin = True,
				student_count = app.user.models.get_total_user_count(),
				classes=app.assignments.models.get_all_class_info(),
				library= ClassLibraryFile.query.all(),
				assignments = Assignment.query.all(),
				active_user_count = app.user.models.get_active_user_count (),
				total_library_downloads = app.files.models.get_total_library_downloads_count (),
				greeting = greeting
			)
		else:
			# Display help message if a student has signed up and is not part of a class
			if Enrollment.query.filter(Enrollment.user_id==current_user.id).first() is None:
				flash('You do not appear to be part of a class. Please contact your tutor for assistance.', 'warning')
				return render_template('index.html')
			return render_template(
				'index.html',
				
				# Assignments
				assignments_info = app.assignments.models.get_user_assignment_info (current_user.id),
				number_of_uploads = app.files.models.get_uploaded_file_count_from_user_id(current_user.id),
				upload_progress_percentage = app.assignments.models.get_assignment_upload_progress_bar_percentage (current_user.id),
				last_upload_humanized_timestamp = app.assignments.models.last_uploaded_assignment_timestamp (current_user.id),
							
				# Peer reviews
				peer_review_progress_percentage = app.assignments.models.get_peer_review_progress_bar_percentage(current_user.id),
				total_completed_peer_reviews = app.assignments.models.get_total_completed_peer_reviews (current_user.id),
				number_of_peer_reviews_on_own_uploads = app.assignments.models.get_received_peer_review_count (current_user.id),
				received_peer_review_count = app.assignments.models.get_received_peer_review_count (current_user.id),
				last_received_peer_review_humanized_timestamp = app.assignments.models.last_incoming_peer_review_timestamp (current_user.id),
				
				# Library
				library_file_count = len(app.files.models.get_user_library_books_from_id (current_user.id)),
				library_download_stat = app.files.models.get_total_downloads_for_user (current_user.id),
				
				# Attendance
				attendance_stats_percentage = app.classes.models.get_user_attendance_record_stats (current_user.id, percentage = True),
				attendance_stats = app.classes.models.get_user_attendance_record_stats (current_user.id),
				
				# Greeting
				greeting = greeting
			)
	
	return render_template('index.html')


# Redirect for lesson registration
@bp.route('/attend')
def lesson_registration_redirect():
	return redirect(url_for('classes.enter_attendance_code'))


# Terms of the website
@bp.route('/terms')
def terms():
	return render_template('terms.html')
