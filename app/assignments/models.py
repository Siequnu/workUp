from app import db
import app.models
from app.models import Upload, Download, Assignment, User, Comment, AssignmentTaskFile
from app.files import models
import datetime, time
from datetime import datetime, date
from dateutil import tz
from flask_login import current_user
import arrow

def get_all_assignments_info (): 
	return db.session.query(Assignment, User).join(User, Assignment.created_by_id == User.id).all()

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
		
	assignment = Assignment(title=form.title.data, description=form.description.data, due_date=form.due_date.data,
						target_turma_id=form.target_turma_id.data, created_by_id=current_user.id,
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

def get_assignments_from_turma_id (turma_id):
	return Assignment.query.filter_by(target_turma_id=turma_id).all()

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
	
def get_user_assignment_info (user_id):
	turma_id = User.get_user_turma_from_user_id (user_id)
	assignments = get_assignments_from_turma_id (turma_id)	
	clean_assignments_array = []
	for assignment in assignments:
		# Convert each SQL object into a  __dict__, then add extra keys for the template
		assignment_dict = assignment.__dict__
		
		assignment_dict['assignment_is_past_deadline'] = check_if_assignment_is_over(assignment_dict['id'])
		assignment_dict['humanized_due_date'] = arrow.get(assignment_dict['due_date']).humanize()
		print (assignment_dict)
		# If user has submitted assignment, get original filename
		if Upload.query.filter_by(assignment_id=assignment_dict['id']).filter_by(user_id=user_id).first() is not None:
			assignment_dict['submitted_filename']= Upload.query.filter_by(
				assignment_id=assignment_dict['id']).filter_by(user_id=user_id).first().original_filename
			
			# Check for uploaded or pending peer-reviews
			# This can either be 0 pending and 0 complete, 0/1 pending and 1 complete, or 0 pending and 2 complete
			completeCount = Comment.getCountCompleteCommentsFromUserIdAndAssignmentId (user_id, assignment_dict['id'])
			assignment_dict['complete_peer_review_count'] = completeCount[0][0]
			
		clean_assignments_array.append(assignment_dict)
	
	return clean_assignments_array

def get_received_peer_review_count (user_id):
	return db.session.query(Comment).join(
		Upload, Comment.file_id==Upload.id).filter(Upload.user_id==user_id).count()

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