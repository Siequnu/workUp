from app import db
import app.models
from app.models import Upload, Download, Assignment, User, Comment
import datetime
from datetime import datetime
import time
from flask_login import current_user

def get_all_assignments_info ():
	assignments = app.models.selectFromDb(['*'], 'assignment')
	# [(1, u'title', u'descrip', u'2018-03-02 00:00:00.000000', 1, u'30640192-1', u'2018-02-28 13:05:59.287555')]
	cleanAssignmentsArray = []
	for assignment in assignments:
		cleanAssignment = {} 
		cleanAssignment['assignmentId'] = assignment[0]
		cleanAssignment['assignmentTitle'] = assignment[1]
		cleanAssignment['assignmentDescription'] = assignment[2]
		cleanAssignment['assignmentDue'] = datetime.strptime(assignment[3], '%Y-%m-%d').date()
		# Try and replace the user id with a username (if fails, user might have been deleted)
		try:
			conditions = []
			conditions.append (str('id="' + str(assignment[4]) + '"'))
			username = app.models.selectFromDb(['username'], 'user', conditions)
			cleanAssignment['assignmentCreatedBy'] = username[0][0]
		except:
			cleanAssignment['assignmentCreatedBy'] = assignment[4]
		cleanAssignment['assignmentForTurmaId'] = assignment[5]
		cleanAssignment['assignmentCreationTimestamp'] = datetime.strptime(assignment[6], '%Y-%m-%d %H:%M:%S.%f').date()
		cleanAssignment['peer_review_necessary'] = assignment[7]
		cleanAssignment['assignmentPeerReviewForm'] = assignment[8]
		cleanAssignmentsArray.append(cleanAssignment)
		
	return cleanAssignmentsArray

def delete_assignment_from_id (assignment_id):
	return Assignment.delete_assignment_from_id(assignment_id)

def get_assignments_from_turma_id (turma_id):
	conditions = []
	conditions.append (str('target_course="' + str(turma_id) + '"'))
	return app.models.selectFromDb(['*'], 'assignment', conditions)

def getAssignmentDueDateFromId (assignmentId):
	conditions = []
	conditions.append (str('id="' + str(assignmentId) + '"'))
	return app.models.selectFromDb(['due_date'], 'assignment', conditions)

def checkIfAssignmentIsOver (assignmentId):
	# Get due date from assignmentId
	conditions = []
	conditions.append (str('id="' + str(assignmentId) + '"'))
	dueDate = app.models.selectFromDb(['due_date'], 'assignment', conditions)
	# Format of date/time strings
	dateFormat = "%Y-%m-%d"
	# Create datetime objects from the strings
	dueDate = datetime.strptime(dueDate[0][0], dateFormat)
	now = datetime.strptime(time.strftime(dateFormat), dateFormat)
	
	if dueDate >= now:
		# Assignment is still open
		return False
	else:
		# Assignment closed
		return True
	
def get_user_assignment_info (user_id):
	turma_id = User.get_user_turma_from_user_id (user_id)
	assignments = get_assignments_from_turma_id (turma_id)
	clean_assignments_array = []
	# Check if user has completed their assignments
	for assignment in assignments:
		clean_assignment = {} 
		clean_assignment['assignmentId'] = assignment[0]
		clean_assignment['assignmentTitle'] = assignment[1]
		clean_assignment['assignmentDescription'] = assignment[2]
		clean_assignment['assignmentDue'] = datetime.strptime(assignment[3], '%Y-%m-%d').date()
		clean_assignment['peer_review_necessary'] = assignment[7]
		clean_assignment['assignmentIsPastDeadline'] = checkIfAssignmentIsOver(assignment[0])
		
		getSubmittedFileId = str(Assignment.getUsersUploadedAssignmentsFromAssignmentId(assignment[0], user_id)) # [(30,)]
		if getSubmittedFileId != '[]': # If user has submitted an upload for this reception
			cleanSubmittedFileId = getSubmittedFileId.replace ('(', '')
			cleanSubmittedFileId = cleanSubmittedFileId.replace (',', '')
			cleanSubmittedFileId = cleanSubmittedFileId.replace (')', '')
			cleanSubmittedFileId = cleanSubmittedFileId.replace (']', '')
			cleanSubmittedFileId = cleanSubmittedFileId.replace ('[', '')
			uploadOriginalFilename = app.models.selectFromDb(['original_filename'], 'upload', [''.join(('id=', str(cleanSubmittedFileId)))])
			clean_assignment['submittedFilename'] = uploadOriginalFilename[0][0]
			
			# Check for uploaded or pending peer-reviews
			# This can either be 0 pending and 0 complete, 0/1 pending and 1 complete, or 0 pending and 2 complete
			completeCount = Comment.getCountCompleteCommentsFromUserIdAndAssignmentId (user_id, assignment[0])
			clean_assignment['completePeerReviewCount'] = completeCount[0][0]
			
		clean_assignments_array.append(clean_assignment)
	
	return clean_assignments_array

def getAssignmentUploadProgressPercentage ():
	# Get turmaId for this user
	turmaId = User.get_user_turma_from_user_id (current_user.id)
	
	# Get assignments due for this user
	assignmentsInfo = get_assignments_from_turma_id(turmaId)
	assignmentsForThisUser = []
	for assignment in assignmentsInfo:
		assignmentId = str(assignment[0])
		assignmentsForThisUser.append(assignmentId)
	
	# Check if user has uploaded each assignment
	completedAssignments = 0
	for assignmentId in assignmentsForThisUser:
		userUploadedAssignmentId = Assignment.getUsersUploadedAssignmentsFromAssignmentId (assignmentId, current_user.id)
		if userUploadedAssignmentId:
			completedAssignments += 1
	
	# Set value of assignment upload progress bar
	if (len(assignmentsForThisUser) != 0):
		assignmentUploadProgressBarPercentage = int(float(completedAssignments)/float(len(assignmentsForThisUser)) * 100)
	else:
		assignmentUploadProgressBarPercentage = 100
	
	return assignmentUploadProgressBarPercentage
	
def getPeerReviewProgressPercentage ():
	# Get turmaId for this user
	turmaId = User.get_user_turma_from_user_id (current_user.id)
	
	# Get assignments due for this user
	assignmentsInfo = get_assignments_from_turma_id(turmaId)
	assignmentsForThisUser = []
	for assignment in assignmentsInfo:
		assignmentId = str(assignment[0])
		assignmentsForThisUser.append(assignmentId)
	
	totalNumberOfPeerReviewsExpected = (len(assignmentsForThisUser)) * 2 # At two peer reviews per assignment
	conditions = []
	conditions.append(''.join(('user_id=', str(current_user.id)))	)
	conditions.append('pending=0')
	commentIds = app.models.selectFromDb(['id'], 'comment', conditions)
	totalNumberOfCompletedPeerReviews = (len(commentIds))
	
	if totalNumberOfPeerReviewsExpected != 0:
		peerReviewProgressBarPercentage = int(float(totalNumberOfCompletedPeerReviews)/float(totalNumberOfPeerReviewsExpected) * 100)
	else:
		peerReviewProgressBarPercentage = 100
		
	return peerReviewProgressBarPercentage