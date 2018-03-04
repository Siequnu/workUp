from app import workUpApp, db
from app.models import Post, Download, Assignment, User
import datetime

def getAllAssignments ():
	assignments = Assignment.getAllAssignments()
	# [(1, u'title', u'descrip', u'2018-03-02 00:00:00.000000', 1, u'30640192-1', u'2018-02-28 13:05:59.287555')]
	cleanAssignmentsArray = []
	for assignment in assignments:
		cleanAssignment = {} 
		cleanAssignment['assignmentId'] = assignment[0]
		cleanAssignment['assignmentTitle'] = assignment[1]
		cleanAssignment['assignmentDescription'] = assignment[2]
		cleanAssignment['assignmentDue'] = datetime.datetime.strptime(assignment[3], '%Y-%m-%d').date()
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
		cleanAssignment['assignmentDue'] = datetime.datetime.strptime(assignment[3], '%Y-%m-%d').date()
		
		getSubmittedFileId = str(Assignment.getUsersUploadedAssignmentsFromAssignmentId(assignment[0], userId)) # [(30,)]
		if getSubmittedFileId != '[]': # If user has submitted an upload for this reception
			cleanSubmittedFileId = getSubmittedFileId.replace ('(', '')
			cleanSubmittedFileId = cleanSubmittedFileId.replace (',', '')
			cleanSubmittedFileId = cleanSubmittedFileId.replace (')', '')
			cleanSubmittedFileId = cleanSubmittedFileId.replace (']', '')
			cleanSubmittedFileId = cleanSubmittedFileId.replace ('[', '')
			postOriginalFilename = Post.getPostOriginalFilenameFromPostId (cleanSubmittedFileId)
			cleanAssignment['submittedFilename'] = postOriginalFilename[0]
			
		cleanAssignmentsArray.append(cleanAssignment)
	
	return cleanAssignmentsArray