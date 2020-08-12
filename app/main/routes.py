from flask import render_template, flash, current_app, session, request, redirect, url_for, abort
from flask_login import current_user, login_required

import datetime

from app.models import Assignment, Enrollment, ClassLibraryFile, Assignment, StatementProject, Inquiry, Feedback
import app.assignments.models
import app.files.models
from app import db
from app.main import bp
import app.user

# Statements
try:
	import app.consultations.models
except:
	pass

# Goals
try:
	import app.goals.models
except:
	pass

# Mentors
try:
	import app.mentors.models
except:
	pass


@current_app.before_request
def before_request():
	if current_user.is_authenticated:
		if app.files.models.new_library_files_since_last_seen():
			flash('New library files have been uploaded', 'info')
		current_user.last_seen = datetime.datetime.now()
		db.session.commit()

# Main entrance to the app


@bp.route('/')
@bp.route('/index')
def index():
	# Dynamically generate the index template name based on app name
	index_template = str('index_') + current_app.config['APP_NAME'] + '.html'

	if current_user.is_authenticated:
		# All models get the greeting
		greeting = app.main.models.get_greeting()

		# For admin views
		if app.models.is_admin(current_user.username):
			return render_template(
				index_template, admin=True,
				greeting=greeting,

				# Student count and info
				active_user_count=app.user.models.get_active_user_count(),
				student_count=app.user.models.get_total_user_count(),
				classes=app.assignments.models.get_all_class_info(),

				# Library
				library=ClassLibraryFile.query.all(),
				total_library_downloads=app.files.models.get_total_library_downloads_count(),

				# Assignments
				assignments=Assignment.query.all(),

				# Statements
				statement_projects=StatementProject.query.all(
				) if app.main.models.is_active_service('app.statements') else False,
				statement_projects_needing_review=app.statements.models.get_projects_needing_review(
				) if app.main.models.is_active_service('app.statements') else False,

			)
		# Student views
		else:
			# Display help message if a student has signed up and is not part of a class
			if Enrollment.query.filter(Enrollment.user_id == current_user.id).first() is None:
				flash(
					'You do not appear to be part of a class. Please contact your tutor for assistance.', 'warning')
				return render_template(index_template)
			return render_template(
				index_template,

				# Assignments
				assignments_info=app.assignments.models.get_user_assignment_info(
					current_user.id),
				number_of_uploads=app.files.models.get_uploaded_file_count_from_user_id(
					current_user.id),
				upload_progress_percentage=app.assignments.models.get_assignment_upload_progress_bar_percentage(
					current_user.id),
				last_upload_humanized_timestamp=app.assignments.models.last_uploaded_assignment_timestamp(
					current_user.id),

				# Peer reviews
				peer_review_progress_percentage=app.assignments.models.get_peer_review_progress_bar_percentage(
					current_user.id),
				total_completed_peer_reviews=app.assignments.models.get_total_completed_peer_reviews(
					current_user.id),
				number_of_peer_reviews_on_own_uploads=app.assignments.models.get_received_peer_review_count(
					current_user.id),
				received_peer_review_count=app.assignments.models.get_received_peer_review_count(
					current_user.id),
				last_received_peer_review_humanized_timestamp=app.assignments.models.last_incoming_peer_review_timestamp(
					current_user.id),

				# Library
				library_file_count=len(
					app.files.models.get_user_library_books_from_id(current_user.id)),
				library_download_stat=app.files.models.get_total_downloads_for_user(
					current_user.id),

				# Attendance
				attendance_stats_percentage=app.classes.models.get_user_attendance_record_stats(
					current_user.id, percentage=True),
				attendance_stats=app.classes.models.get_user_attendance_record_stats(
					current_user.id),

				# Greeting
				greeting=greeting,

				# Consultations
				consultations=app.consultations.models.get_consultation_info_array(
					current_user.id) if app.main.models.is_active_service('app.consultations') else False,

				# Goals
				goals=app.goals.models.get_student_goals_from_user_id(
						current_user.id) if app.main.models.is_active_service('app.goals') else False,

				# Mentors
				mentors=app.mentors.models.get_mentors_from_student_id(
						current_user.id) if app.main.models.is_active_service('app.mentors') else False
			)

	if current_app.config['APP_NAME'] == 'workUp':
		return render_template('product.html')
	elif current_app.config['APP_NAME'] == 'elmOnline':
		return render_template('elm_product.html')
	else:
		return render_template(index_template)


# Redirect for lesson registration
@bp.route('/attend')
def lesson_registration_redirect():
	return redirect(url_for('classes.enter_attendance_code'))

# workUp specific routing
# Features of the website


@bp.route('/product')
def product():
	if current_app.config['APP_NAME'] == 'workUp':
		return render_template('product.html')
	else:
		return redirect(url_for('main.index'))

@bp.route('/teachers')
def product_teachers():
	if current_app.config['APP_NAME'] == 'workUp':
		return render_template('teachers.html')
	else:
		return redirect(url_for('main.index'))

@bp.route('/consultancies')
def product_consultancies():
	if current_app.config['APP_NAME'] == 'workUp':
		return render_template('consultancies.html')
	else:
		return redirect(url_for('main.index'))

# URL for UK contract purposes
@bp.route('/features')
def features():
	return redirect(url_for('main.index'))

# URL for THU feedback
@bp.route('/feedback', methods=['GET', 'POST'])
def feedback():
	if current_app.config['APP_NAME'] == 'workUp':
		if request.method == 'POST':
			feedback = Feedback(
				loved=request.form.get('loved'),
				improve=request.form.get('improve'),
				learn=request.form.get('learn'),
				valuable=request.form.get('valuable'),
				timestamp=datetime.datetime.now()
			)
			feedback.save()
			# ¡# Send email to to admin?
			flash(
				'Thank you for your feedback. See you soon!', 'success')
			return redirect(url_for('main.product'))
		else: 
			return render_template('feedback.html')
	else:
		return redirect(url_for('main.index'))

# Inquiry form
@bp.route('/feedback/view')
@login_required
def view_feedback():
	if current_app.config['APP_NAME'] == 'workUp':
		if app.models.is_admin(current_user.username):
			feedbacks = Feedback.query.all()
			return render_template('view_feedback.html', feedbacks=feedbacks)
	return redirect(url_for('main.index'))

# Inquiry form
@bp.route('/feedback/delete/<feedback_id>')
@login_required
def delete_feedback(feedback_id):
	if current_app.config['APP_NAME'] == 'workUp':
		if app.models.is_admin(current_user.username):
			feedback = Feedback.query.get(feedback_id)
			feedback.delete()
			flash('Removed the feedback.', 'success')
			return redirect(url_for('main.view_feedback'))
	else:
		return redirect(url_for('main.index'))


@bp.route('/inquire', methods=['GET', 'POST'])
def inquire():
	if current_app.config['APP_NAME'] == 'workUp':
		if request.method == 'POST':
			inquiry = Inquiry(
				name=request.form.get('name'),
				email=request.form.get('email-address'),
				message=request.form.get('message'),
				timestamp=datetime.datetime.now()
			)
			inquiry.save()
			# ¡# Send email to to admin?
			flash(
				'Thank you! We have received your enquiry and will be in touch soon.', 'success')
			return redirect(url_for('main.product'))
		else: 
			return render_template('inquire.html')
	else:
		return redirect(url_for('main.index'))

# Inquiry form
@bp.route('/inquiries/view', methods=['GET', 'POST'])
@login_required
def view_inquiries():
	if current_app.config['APP_NAME'] == 'workUp':
		if app.models.is_admin(current_user.username):
			inquiries = Inquiry.query.all()
			return render_template('view_inquiries.html', inquiries=inquiries)
	return redirect(url_for('main.index'))

# Inquiry form
@bp.route('/inquiries/delete/<inquiry_id>')
@login_required
def delete_inquiry(inquiry_id):
	if current_app.config['APP_NAME'] == 'workUp':
		if app.models.is_admin(current_user.username):
			inquiry = Inquiry.query.get(inquiry_id)
			inquiry.delete()
			flash('Removed the inquiry.', 'success')
			return redirect(url_for('main.view_inquiries'))
	else:
		return redirect(url_for('main.index'))

# elmOnline specific routing
# Page that displays the QR code

@bp.route('/contact')
def contact():
	if current_app.config['APP_NAME'] == 'elmOnline':
		return render_template('contact.html')
	else:
		return redirect(url_for('main.index'))

@bp.route('/admissions')
def elm_admissions():
	if current_app.config['APP_NAME'] == 'elmOnline': return render_template('elm_admissions.html')
	else: return redirect(url_for('main.index'))

@bp.route('/elm/inquire', methods=['GET', 'POST'])
def elm_inquire():
	if current_app.config['APP_NAME'] == 'elmOnline':
		if request.method == 'POST':
			inquiry = Inquiry(
				name=request.form.get('name'),
				email=request.form.get('email-address'),
				message=request.form.get('message'),
				timestamp=datetime.datetime.now()
			)
			inquiry.save()
			# ¡# Send email to to admin?
			flash(
				'Thank you! We have received your enquiry and will be in touch soon.', 'success')
			return redirect(url_for('main.index'))
		else: 
			return render_template('elm_inquire.html')
	else:
		return redirect(url_for('main.index'))