from flask_login import current_user

import app.models
from app import db
from app.models import Upload, Download, Assignment, User, Comment, AssignmentTaskFile, Turma, Enrollment, PeerReviewForm
from app.files import models

from datetime import datetime, date
from dateutil import tz
import arrow, json, time

def get_assignment_info (assignment_id = False): 
	assignments_array = []
	if assignment_id:
		assignment_info = db.session.query(Assignment, User, Turma).join(
		User, Assignment.created_by_id == User.id).join(
		Turma, Assignment.target_turma_id==Turma.id).filter(Assignment.id == assignment_id).all()
	else:
		assignment_info = db.session.query(Assignment, User, Turma).join(
		User, Assignment.created_by_id == User.id).join(
		Turma, Assignment.target_turma_id==Turma.id).all()
	
	for assignment, user, turma in assignment_info:
		students_in_class = Enrollment.query.filter(Enrollment.turma_id == turma.id).all()
		completed_assignments = Upload.query.filter(Upload.assignment_id == assignment.id).all()
		uncomplete_assignments = len(students_in_class) - len(completed_assignments)
		if assignment.peer_review_necessary == True:
			peer_review_form_title = PeerReviewForm.query.get(assignment.peer_review_form_id).title
		else:
			peer_review_form_title = False
		if assignment.assignment_task_file_id is not None:
			try:
				assignment_task_filename = AssignmentTaskFile.query.get(assignment.assignment_task_file_id).original_filename
			except:
				assignment_task_filename = False
		else:
			assignment_task_filename = False
		assignment_dict = assignment, user, turma, completed_assignments, uncomplete_assignments, assignment_task_filename, peer_review_form_title, students_in_class
		assignments_array.append (assignment_dict)
	return assignments_array

# Returns array of all students in class with added assignment info if applicable
def get_assignment_student_info (assignment_id):
	assignment = Assignment.query.get(assignment_id)
	turma_id = assignment.target_turma_id
	students = db.session.query(User).join(
		Enrollment, User.id == Enrollment.user_id).filter(
		Enrollment.turma_id == turma_id).order_by(User.student_number.asc()).all()
	assignment_detail_info = []
	for student in students:
		student_dict = student.__dict__
		try:
			student_dict['upload'] = db.session.query(Upload).filter(
			Upload.user_id == student_dict['id']).filter(
			Upload.assignment_id == assignment_id).first()
		except:
			pass
		try:
			student_dict['comments'] = db.session.query(Comment).filter(
			Comment.file_id == student_dict['upload'].id).filter(Comment.pending == 0).all()
		except:
			pass
		assignment_detail_info.append(student_dict)
	return assignment_detail_info
	

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

def get_user_assignment_info (user_id, assignment_id = False):
	
	assignments = []
	if assignment_id:
		assignments.append(Assignment.query.get(assignment_id))
	else:
		# Get user enrollment, then fetch and compile assignments for each class
		turma_ids = db.session.query(
			User, Enrollment).join(
			Enrollment, User.id == Enrollment.user_id).filter(
			User.id==user_id).all()
		for user, enrollment in turma_ids:
			assignments_array = get_assignments_from_turma_id (enrollment.turma_id)
			for assignment in assignments_array:
				assignments.append (assignment)
	
	clean_assignments_array = []
	for assignment in assignments:
		# Convert each SQL object into a  __dict__, then add extra keys for the template
		assignment_dict = assignment.__dict__
		
		assignment_dict['assignment_is_past_deadline'] = check_if_assignment_is_over(assignment_dict['id'])
		assignment_dict['humanized_due_date'] = arrow.get(assignment_dict['due_date']).humanize()
		
		if assignment_dict['assignment_task_file_id'] is not None:
			assignment_dict['assignment_task_filename'] = AssignmentTaskFile.query.get(assignment_dict['assignment_task_file_id']).original_filename
		else:
			assignment_dict['assignment_task_filename'] = False
		
		# If user has submitted assignment, get original filename
		if Upload.query.filter_by(assignment_id=assignment_dict['id']).filter_by(user_id=user_id).first() is not None:
			assignment_dict['submitted_filename']= Upload.query.filter_by(
				assignment_id=assignment_dict['id']).filter_by(user_id=user_id).first().original_filename
			#!# Why not just sent the whole upload. Pages looking for submitted_filename can just open the upload object
			assignment_dict['upload'] = Upload.query.filter_by(
				assignment_id=assignment_dict['id']).filter_by(user_id=user_id).first()
			# Check for uploaded or pending peer-reviews
			# This can either be 0 pending and 0 complete, 0/1 pending and 1 complete, or 0 pending and 2 complete
			completed_peer_reviews = Comment.get_completed_peer_reviews_from_user_for_assignment (user_id, assignment_dict['id'])
			assignment_dict['complete_peer_review_count'] = len(completed_peer_reviews)
			assignment_dict['completed_peer_review_objects'] = completed_peer_reviews
			
		clean_assignments_array.append(assignment_dict)
	if assignment_id:
		# Just return the first result
		return clean_assignments_array.pop()
	else: # Return an array of all assignments
		return clean_assignments_array

def get_peer_review_form_from_upload_id (upload_id):
	return db.session.query(
		Assignment).join(
		Upload,Assignment.id==Upload.assignment_id).filter(
		Upload.id == upload_id).first().peer_review_form_id

def get_received_peer_review_count (user_id):
	return db.session.query(Comment).join(
		Upload, Comment.file_id==Upload.id).filter(Upload.user_id==user_id).count()

def get_assignment_upload_progress_bar_percentage (user_id):
	assignments_for_user = len(db.session.query(Assignment, Enrollment).join(
		Enrollment, Assignment.target_turma_id == Enrollment.turma_id).filter(
		Enrollment.user_id == user_id).all())

	completed_assignments = db.session.query(Assignment).join(
		Upload, Assignment.id==Upload.assignment_id).filter(Upload.user_id==current_user.id).count()
	if assignments_for_user > 0:
		return int(float(completed_assignments)/float(assignments_for_user) * 100)
	else:
		return 100
	
def get_peer_review_progress_bar_percentage (user_id):
	peer_review_assignments_for_user = len(db.session.query(Assignment, Enrollment).join(
		Enrollment, Assignment.target_turma_id == Enrollment.turma_id).filter(
		Enrollment.user_id == user_id).filter(Assignment.peer_review_necessary == True).all())
	
	total_peer_reviews_expected = peer_review_assignments_for_user * 2 # At two peer reviews per assignment
	
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
	
	for turma_id in form.target_turmas.data:
		assignment = Assignment(title=form.title.data, description=form.description.data, due_date=form.due_date.data,
						target_turma_id=turma_id, created_by_id=current_user.id,
						peer_review_necessary= form.peer_review_necessary.data,
						peer_review_form_id=form.peer_review_form_id.data)
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
	db.session.flush() # Access the new comment ID
	new_comment_id = comment.id
	db.session.commit()
	return new_comment_id

def delete_all_comments_from_upload_id (upload_id):
	comments = Comment.query.filter_by(file_id=upload_id).all()
	if comments is not None:
		for comment in comments:
			db.session.delete(comment)
	db.session.commit()

def delete_all_comments_from_user_id (user_id):
	comments = Comment.query.filter_by(user_id=user_id).all()
	if comments is not None:
		for comment in comments:
			db.session.delete(comment)
	db.session.commit()


def new_peer_review_from_form (form_contents, assignment_id):
	# Check if user has any previous downloads with pending peer reviews
	pending_assignment = Comment.get_pending_status_from_user_id_and_assignment_id (current_user.id, assignment_id)
	if pending_assignment is not None:
		# User has a pending peer review - update the empty comment field with the contents of this form and remove pending status
		# If there is no pending status - user has not yet downloaded a file, so don't accept the review
		Comment.update_pending_comment_with_contents(pending_assignment.id, form_contents)
		return True
	else:
		return False
		

def check_if_assignment_is_over (assignment_id):
	due_date = Assignment.query.get(assignment_id).due_date
	due_datetime = datetime(due_date.year, due_date.month, due_date.day)
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

