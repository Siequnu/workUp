from app import db
import app.models
from app.models import Upload, Download, Assignment, User, Comment, AssignmentTaskFile
import datetime
from datetime import datetime, date
import time
from flask_login import current_user
from sqlalchemy import text

def get_all_assignments_info (): 
	return db.session.query(
		Assignment, User).join(
		User, Assignment.created_by_id == User.id).all()

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
	dueDate = Assignment.query.get(assignment_id).due_date
	dueDatetime = datetime(dueDate.year, dueDate.month, dueDate.day)
	# Format of date/time strings
	dateFormat = "%Y-%m-%d"
	# Create datetime objects from the strings
	now = datetime.strptime(time.strftime(dateFormat), dateFormat)
	
	if dueDatetime >= now: # Assignment is still open
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

def get_assignment_upload_progress_bar_percentage ():
	turma_id = User.get_user_turma_from_user_id (current_user.id)	
	assignments_for_user = Assignment.query.filter_by(target_turma_id=turma_id).all()
	
	# Check if user has uploaded each assignment
	#!# This can be achieved in a single SQL Query using JOIN and COUNT?
	completed_assignments = 0
	for assignment in assignments_for_user:
		if Upload.query.filter_by(assignment_id=assignment.id).filter_by(user_id=current_user.id).first() is not None:
			completed_assignments += 1
	# Set value of assignment upload progress bar
	if (len(assignments_for_user) > 0):
		return int(float(completed_assignments)/float(len(assignments_for_user)) * 100)
	else:
		return 100
	
def get_peer_review_progress_bar_percentage ():
	turma_id = User.get_user_turma_from_user_id (current_user.id)
	assignments_for_user = Assignment.query.filter_by(target_turma_id=turma_id).all()
	
	total_peer_reviews_expected = (len(assignments_for_user)) * 2 # At two peer reviews per assignment
	#!# What about non-peer review assignments? Cross check with needs_peer_review
	total_completed_peer_reviews = len(Comment.query.filter_by(user_id=current_user.id).filter_by(pending=False).all())
	
	if total_peer_reviews_expected > 0:
		return int(float(total_completed_peer_reviews)/float(total_peer_reviews_expected) * 100)
	else:
		return 100