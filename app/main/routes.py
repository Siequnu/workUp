from flask import render_template, flash, current_app, session
from flask_login import current_user, login_required

import datetime

from app.models import Assignment, Enrollment, ClassLibraryFile, Assignment
import app.assignments.models
from app import db
from app.main import bp
import app.user

@current_app.before_request
def before_request():
	if current_user.is_authenticated:
		current_user.last_seen = datetime.datetime.now()
		db.session.commit()

# Main entrance to the app
@bp.route('/', methods=['GET', 'POST'])
@bp.route('/index', methods=['GET', 'POST'])
def index():
	if current_user.is_authenticated:
		if app.models.is_admin(current_user.username):
			return render_template('index.html', admin = True,
								   student_count = app.user.models.get_total_user_count(),
								   classes=app.assignments.models.get_all_class_info(),
								   library= ClassLibraryFile.query.all(),
								   assignments = Assignment.query.all())
		else:
			# Display help message if a student has signed up and is not part of a class
			if Enrollment.query.filter(Enrollment.user_id==current_user.id).first() is None:
				flash('You do not appear to be part of a class. Please contact your tutor for assistance.', 'warning')
				return render_template('index.html')			
			return render_template('index.html',
							number_of_uploads = app.files.models.get_uploaded_file_count_from_user_id(current_user.id),
							upload_progress_percentage = app.assignments.models.get_assignment_upload_progress_bar_percentage (current_user.id),
							peer_review_progress_percentage = app.assignments.models.get_peer_review_progress_bar_percentage(current_user.id),
							number_of_peer_reviews_on_own_uploads = app.assignments.models.get_received_peer_review_count (current_user.id),
							last_upload_humanized_timestamp = app.assignments.models.last_uploaded_assignment_timestamp (current_user.id),
							last_received_peer_review_humanized_timestamp = app.assignments.models.last_incoming_peer_review_timestamp (current_user.id),
							assignments_info = app.assignments.models.get_user_assignment_info (current_user.id))
	
	return render_template('index.html')
