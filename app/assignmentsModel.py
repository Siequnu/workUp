from app import workUpApp, db
import app.models
from app.models import Post, Download, Assignment, User, Comment
import datetime
from datetime import datetime
import time
import string

def getAllAssignments ():
	assignments = Assignment.getAllAssignments()
	# [(1, u'title', u'descrip', u'2018-03-02 00:00:00.000000', 1, u'30640192-1', u'2018-02-28 13:05:59.287555')]
	cleanAssignmentsArray = []
	for assignment in assignments:
		cleanAssignment = {} 
		cleanAssignment['assignmentId'] = assignment[0]
		cleanAssignment['assignmentTitle'] = assignment[1]
		cleanAssignment['assignmentDescription'] = assignment[2]
		cleanAssignment['assignmentDue'] = datetime.strptime(assignment[3], '%Y-%m-%d').date()
		cleanAssignment['assignmentCreatedBy'] = assignment[4]
		cleanAssignment['assignmentForTurmaId'] = assignment[5]
		cleanAssignment['assignmentCreationTimestamp'] = assignment[6]
		cleanAssignment['assignmentPeerReviewForm'] = assignment[7]
		cleanAssignmentsArray.append(cleanAssignment)
	
	return cleanAssignmentsArray
	
def getUserTurmaFromId (userId):
	return User.getUserTurmaFromId(userId)

def deleteAssignmentFromId (assignmentId):
	return Assignment.deleteAssignmentFromId(assignmentId)

def getAssignmentsFromTurmaId (turmaId):
	return Assignment.getAssignmentsFromTurmaId (str(turmaId[0]))

def getAssignmentDueDateFromId (assignmentId):
	return Assignment.getAssignmentDueDateFromId (assignmentId)

def checkIfAssignmentIsOver (assignmentId):
	# Get due date from assignmentId
	dueDate = Assignment.getAssignmentDueDateFromId (assignmentId)
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
	
def getUserAssignmentInformation (userId):
	turmaId = getUserTurmaFromId (userId)
	assignments = getAssignmentsFromTurmaId (turmaId)
	cleanAssignmentsArray = []
	# Check if user has completed their assignments
	for assignment in assignments:
		cleanAssignment = {} 
		cleanAssignment['assignmentId'] = assignment[0]
		cleanAssignment['assignmentTitle'] = assignment[1]
		cleanAssignment['assignmentDescription'] = assignment[2]
		cleanAssignment['assignmentDue'] = datetime.strptime(assignment[3], '%Y-%m-%d').date()
		cleanAssignment['assignmentIsPastDeadline'] = checkIfAssignmentIsOver(assignment[0])
		
		getSubmittedFileId = str(Assignment.getUsersUploadedAssignmentsFromAssignmentId(assignment[0], userId)) # [(30,)]
		if getSubmittedFileId != '[]': # If user has submitted an upload for this reception
			cleanSubmittedFileId = getSubmittedFileId.replace ('(', '')
			cleanSubmittedFileId = cleanSubmittedFileId.replace (',', '')
			cleanSubmittedFileId = cleanSubmittedFileId.replace (')', '')
			cleanSubmittedFileId = cleanSubmittedFileId.replace (']', '')
			cleanSubmittedFileId = cleanSubmittedFileId.replace ('[', '')
			postOriginalFilename = app.models.selectFromDb(['original_filename'], 'post', [string.join(('id=', str(cleanSubmittedFileId)), '')])
			cleanAssignment['submittedFilename'] = postOriginalFilename[0][0]
			
			
			# Check for uploaded or pending peer-reviews
			# This can either be 0 pending and 0 complete, 0/1 pending and 1 complete, or 0 pending and 2 complete
			completeCount = Comment.getCountCompleteCommentsFromUserIdAndAssignmentId (userId, assignment[0])
			cleanAssignment['completePeerReviewCount'] = completeCount[0][0]
			
		cleanAssignmentsArray.append(cleanAssignment)
	
	return cleanAssignmentsArray