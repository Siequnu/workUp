from app import db
import app.models
from app.models import Upload, Download, Assignment, User, Comment, AssignmentTaskFile, Turma, Enrollment
from app.files import models
import datetime, time
from datetime import datetime, date
from dateutil import tz
from flask_login import current_user
import arrow, json

def get_all_assignments_info (): 
	return db.session.query(Assignment, User, Turma).join(
		User, Assignment.created_by_id == User.id).join(
		Turma, Assignment.target_turma_id==Turma.id).all()

def get_user_enrollment_from_id (user_id):
	return db.session.query(Enrollment, User, Turma).join(
		User, Enrollment.user_id==User.id).join(
		Turma, Enrollment.turma_id == Turma.id).filter(
		Enrollment.user_id==user_id).all()

def get_all_class_info():
	return Turma.query.all()

def reset_user_enrollment (user_id):
	if Enrollment.query.filter(Enrollment.user_id==user_id).first() is not None:
		Enrollment.query.filter(Enrollment.user_id==user_id).delete()
		db.session.commit()

def enroll_user_in_class (user_id, turma_id):
	
	if Enrollment.query.filter(Enrollment.user_id==user_id).filter(Enrollment.turma_id==turma_id).first() is None:
		new_enrollment = Enrollment(user_id = user_id, turma_id = turma_id)
		db.session.add(new_enrollment)
		db.session.commit()

def get_class_enrollment_from_class_id (class_id):
	return db.session.query(
		Enrollment, Turma, User).join(
		Turma, Enrollment.turma_id==Turma.id).join(
		User, Enrollment.user_id==User.id).filter(
		Enrollment.turma_id == class_id).all()

def get_user_assignment_info (user_id):
	turma_id = User.get_user_turma_from_user_id (user_id)
	assignments = get_assignments_from_turma_id (turma_id)	
	clean_assignments_array = []
	for assignment in assignments:
		# Convert each SQL object into a  __dict__, then add extra keys for the template
		assignment_dict = assignment.__dict__
		
		assignment_dict['assignment_is_past_deadline'] = check_if_assignment_is_over(assignment_dict['id'])
		assignment_dict['humanized_due_date'] = arrow.get(assignment_dict['due_date']).humanize()
		# If user has submitted assignment, get original filename
		if Upload.query.filter_by(assignment_id=assignment_dict['id']).filter_by(user_id=user_id).first() is not None:
			assignment_dict['submitted_filename']= Upload.query.filter_by(
				assignment_id=assignment_dict['id']).filter_by(user_id=user_id).first().original_filename
			
			# Check for uploaded or pending peer-reviews
			# This can either be 0 pending and 0 complete, 0/1 pending and 1 complete, or 0 pending and 2 complete
			completed_peer_reviews = Comment.get_completed_peer_reviews_from_user_for_assignment (user_id, assignment_dict['id'])
			assignment_dict['complete_peer_review_count'] = len(completed_peer_reviews)
			assignment_dict['completed_peer_review_objects'] = completed_peer_reviews
			
		clean_assignments_array.append(assignment_dict)
	
	return clean_assignments_array

def get_peer_review_form_from_upload_id (upload_id):
	return db.session.query(
		Assignment).join(
		Upload,Assignment.id==Upload.assignment_id).filter(
		Upload.id == upload_id).first().peer_review_form

def get_received_peer_review_count (user_id):
	return db.session.query(Comment).join(
		Upload, Comment.file_id==Upload.id).filter(Upload.user_id==user_id).count()

def get_assignment_upload_progress_bar_percentage (user_id):
	turma_id = User.get_user_turma_from_user_id (user_id)	
	assignments_for_user = Assignment.query.filter_by(target_turma_id=turma_id).count()
	completed_assignments = db.session.query(Assignment).join(
		Upload, Assignment.id==Upload.assignment_id).filter(Upload.user_id==current_user.id).count()
	
	if assignments_for_user > 0:
		return int(float(completed_assignments)/float(assignments_for_user) * 100)
	else:
		return 100
	
def get_peer_review_progress_bar_percentage (user_id):
	turma_id = User.get_user_turma_from_user_id (user_id)
	assignments_for_user = Assignment.query.filter_by(target_turma_id=turma_id).count()
	total_peer_reviews_expected = assignments_for_user * 2 # At two peer reviews per assignment
	#!# What about non-peer review assignments? Cross check with needs_peer_review
	total_completed_peer_reviews = Comment.query.filter_by(user_id=user_id).filter_by(pending=False).count()
	if total_peer_reviews_expected > 0:
		return int(float(total_completed_peer_reviews)/float(total_peer_reviews_expected) * 100)
	else:
		return 100
	
def get_comment_author_id_from_comment (comment_id):
	return Comment.query.get(comment_id).user_id

def get_assignments_from_turma_id (turma_id):
	return Assignment.query.filter_by(target_turma_id=turma_id).all()

def new_assignment_from_form (form):
	if form.assignment_task_file.data is not None:
		file = form.assignment_task_file.data
		random_filename = app.files.models.save_file(file)
		original_filename = app.files.models.get_secure_filename(file.filename)
		assignment_task_file = AssignmentTaskFile (original_filename=original_filename,
											   filename = random_filename,
											   user_id = current_user.id)
		db.session.add(assignment_task_file)
		db.session.flush() # Access the assignment_task_file.id field from db
	
	for turma_id in form.target_turma_id.data:
		assignment = Assignment(title=form.title.data, description=form.description.data, due_date=form.due_date.data,
						target_turma_id=turma_id, created_by_id=current_user.id,
						peer_review_necessary= form.peer_review_necessary.data,
						peer_review_form=form.peer_review_form.data)
		if form.assignment_task_file.data is not None:
			assignment.assignment_task_file_id=assignment_task_file.id
	
		db.session.add(assignment)
		db.session.commit()

def delete_assignment_from_id (assignment_id):	
	# Delete assignment_task_file, if it exists
	if db.session.query(Assignment.assignment_task_file_id).filter_by(id=assignment_id).scalar() is not None:
		assignment_task_file_id = Assignment.query.get(assignment_id).assignment_task_file_id
		AssignmentTaskFile.query.filter_by(id=assignment_task_file_id).delete()
	# Delete assignment
	Assignment.query.filter_by(id=assignment_id).delete()
	# Delete all upload records for this assignment
	assignment_uploads = Upload.query.filter_by(assignment_id=assignment_id).all()
	if assignment_uploads is not None:
		for upload in assignment_uploads:
			db.session.delete(upload)
	# Delete all comments for those uploads
	comments = Comment.query.filter_by(assignment_id=assignment_id).all()
	if comments is not None:
		for comment in comments:
			db.session.delete(comment)
	db.session.commit()
	# Download records are not deleted for future reference
	return True

def add_teacher_comment_to_upload (form_contents, upload_id):
	comment = Comment(comment = form_contents, user_id = current_user.id,
					  file_id = upload_id, pending = False, assignment_id = Upload.query.get(upload_id).assignment_id)
	db.session.add(comment)
	db.session.commit()
	return True

def new_peer_review_from_form (form, assignment_id):
	# Serialise the form contents
	form_fields = {}
	for field_title, field_contents in form.data.items():
		form_fields[field_title] = field_contents
	# Clean the csrf_token and submit fields
	del form_fields['csrf_token']
	del form_fields['submit']
	form_contents = json.dumps(form_fields)
	
	# Check if user has any previous downloads with pending peer reviews
	pending_assignments = Comment.getPendingStatusFromUserIdAndAssignmentId (current_user.id, assignment_id)
	if len(pending_assignments) > 0:
		# User has a pending peer review - update the empty comment field with the contents of this form and remove pending status
		# If there is no pending status - user has not yet downloaded a file, so don't accept the review
		pending_comment_id = pending_assignments[0][0]
		update_comment = Comment.update_pending_comment_with_contents(pending_comment_id, form_contents)
		return True
	else:
		return False
		

def check_if_assignment_is_over (assignment_id):
	due_date = Assignment.query.get(assignment_id).due_date
	due_datetime = datetime(due_date.year, due_date.month, due_date.day)
	# Format of date/time strings
	date_format = "%Y-%m-%d"
	# Create datetime objects from the strings
	now = datetime.strptime(time.strftime(date_format), date_format)
	
	if due_datetime >= now: # Assignment is still open
		return False
	else: # Assignment closed
		return True

def last_uploaded_assignment_timestamp (user_id):
	if Upload.query.filter_by(user_id=user_id).order_by(Upload.timestamp.desc()).first() is not None:
		last_upload_timestamp = Upload.query.filter_by(user_id=user_id).order_by(Upload.timestamp.desc()).first().timestamp
		return arrow.get(last_upload_timestamp, tz.gettz('Asia/Hong_Kong')).humanize()
	else: return False

def last_incoming_peer_review_timestamp (user_id):
	if db.session.query(Comment).join(Upload,Comment.file_id==Upload.id).filter(
		Upload.user_id==user_id).order_by(Comment.timestamp.desc()).first() is not None:
		latest_incoming_peer_review = db.session.query(Comment).join(Upload,Comment.file_id==Upload.id).filter(
			Upload.user_id==user_id).order_by(Comment.timestamp.desc()).first().timestamp
		return arrow.get(latest_incoming_peer_review, tz.gettz('Asia/Hong_Kong')).humanize() 
	else: return False	

