from datetime import datetime
from app import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import login
from sqlalchemy import text
import json

@login.user_loader
def load_user(id):
	return User.query.get(int(id))

def is_admin (username):
	# Returns True if user is admin, False if not
	return username in User.get_admin_users_list() 

def selectFromDb (columnsArray, fromTable, conditionsArray = False, count = False):
	# Assemble SQL query from input variables
	if count:
		sqlQuery = 'SELECT COUNT ('
		columnsString = ''
		columnsString = columnsString + columnsArray.pop()
		sqlQuery = sqlQuery + columnsString + ') FROM ' + str(fromTable)
	else:
		sqlQuery = 'SELECT '
		columnsString = ''
		while len(columnsArray) > 1:	
			columnsString = columnsString + columnsArray.pop() + ', '
		columnsString = columnsString + columnsArray.pop()
		sqlQuery = sqlQuery + columnsString + ' FROM ' + str(fromTable)
	
	if conditionsArray:
		conditionsString = ''
		while len(conditionsArray) > 1:	
			conditionsString = conditionsString + conditionsArray.pop() + ' AND '
		conditionsString = conditionsString + conditionsArray.pop()
		sqlQuery = sqlQuery + ' WHERE ' + str(conditionsString)
	
	sql = text(sqlQuery)
	result = db.engine.execute(sql)	
	names = []
	for row in result: names.append(row)
	return names

class Turma(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	turma_number = db.Column(db.String(140), index=True)
	turma_label = db.Column(db.String(280))
	turma_term = db.Column(db.String(140))
	turma_year = db.Column(db.Integer)
	
	def __repr__(self):
		return '<Turma {}>'.format(self.turma_number)

	@staticmethod
	def getTurmaChoiceListForForm ():
		allTurmas = selectFromDb(['*'], 'turma')
		turmaNumberAndLabelList = []
		for turmaInfo in allTurmas:
			turmaNumberAndLabelList.append((turmaInfo[1], turmaInfo[2]))
		return turmaNumberAndLabelList
	
	@staticmethod
	def deleteTurmaFromId (turmaId):
		sql = text ('DELETE FROM turma WHERE id=' + '"' + str(turmaId) + '"')
		result = db.engine.execute(sql)
		return result

	


class User(UserMixin, db.Model):
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(64), index=True, unique=True)
	email = db.Column(db.String(120), index=True, unique=True)
	password_hash = db.Column(db.String(128))
	studentnumber = db.Column(db.String(12))
	turma_id = db.Column(db.String(20))
	last_seen = db.Column(db.DateTime, default=datetime.now)
	registered = db.Column(db.DateTime, default=datetime.now)
	email_confirmed = db.Column(db.Boolean, default=False)
	is_admin = db.Column(db.Boolean, default=False)

	def __repr__(self):
		return '<User {}>'.format(self.username)
	
	def set_password(self, password):
		self.password_hash = generate_password_hash(password)

	def check_password(self, password):
		return check_password_hash(self.password_hash, password)

	@staticmethod
	def checkEmailConfirmationStatus (user):
		sql = text('SELECT email_confirmed FROM user WHERE username ="' + str(user) + '"')
		result = db.engine.execute(sql)
		names = []
		for row in result: names.append(row)
		if names[0][0] == 1:
			return True
		else:
			return False
		
	@staticmethod
	def get_admin_users_list ():
		sql = text('SELECT username FROM user WHERE is_admin ="' + str(1) + '"')
		result = db.engine.execute(sql)
		# Unpack results from sql object
		usernames = []
		for row in result: usernames.append(row)
		# Clean results from tuple to array
		clean_usernames = []
		for username_tuple in usernames: clean_usernames.append(username_tuple[0])
		return clean_usernames
	
	

class Upload(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	original_filename = db.Column(db.String(140))
	filename = db.Column(db.String(140))
	timestamp = db.Column(db.DateTime, index=True, default=datetime.now)
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
	assignment_id = db.Column(db.Integer)
	
	def __repr__(self):
		return '<Upload {}>'.format(self.filename)		
	
	@staticmethod
	def getAllUploadsWithFilenameAndUsername ():
		sql = text('SELECT upload.original_filename, user.username, upload.timestamp FROM upload INNER JOIN user ON user.id=upload.user_id;')
		result = db.engine.execute(sql)
		names = []
		for row in result: names.append(row)
		return names
	
	@staticmethod
	def getPossibleDownloadsNotFromUserForThisAssignment (userId, assignmentId, previousDownloadFileId = False):
		if previousDownloadFileId:
			sql = text ('SELECT filename FROM upload WHERE user_id!=' + str(userId) + ' AND assignment_id=' + str(assignmentId) + ' AND id!=' + str(previousDownloadFileId))
		else:
			sql = text ('SELECT filename FROM upload WHERE user_id!=' + str(userId) + ' AND assignment_id=' + str(assignmentId))
		result = db.engine.execute(sql)
		filenames = []
		for row in result: filenames.append(row[0])
		return filenames
	
	@staticmethod
	def deleteAllUploadsFromAssignmentId (assignmentId):
		sql = text ('DELETE FROM upload WHERE assignment_id=' + '"' + str(assignmentId) + '"')
		result = db.engine.execute(sql)
		return result

	
	
class Download(db.Model):
	
	id = db.Column(db.Integer, primary_key=True)
	filename = db.Column(db.String(140))
	timestamp = db.Column(db.DateTime, index=True, default=datetime.now)
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
	
	def __repr__(self):
		return '<Download {}>'.format(self.filename)
	


class Comment(db.Model):
	
	id = db.Column(db.Integer, primary_key=True)
	comment = db.Column(db.String(140))
	timestamp = db.Column(db.DateTime, index=True, default=datetime.now)
	user_id = db.Column(db.Integer)
	fileid = db.Column(db.Integer)
	pending = db.Column(db.Boolean)
	assignment_id = db.Column(db.String(140))
	
	def __repr__(self):
		return '<Comment {}>'.format(self.comment)
	
	@staticmethod
	def getPendingStatusFromUserIdAndAssignmentId (userId, assignmentId):
		sql = text ('SELECT id, fileid FROM comment WHERE user_id=' + str(userId) + ' AND assignment_id=' + str(assignmentId) + ' AND pending=1')
		result = db.engine.execute(sql)
		names = []
		for row in result: names.append(row)
		return names
	
	@staticmethod
	def updatePendingCommentWithComment (commentId, peerReviewContents):
		sql = text ("UPDATE comment SET pending=0, comment='" + str(peerReviewContents) + "' WHERE id='" + str(commentId) + "'")
		result = db.engine.execute(sql)
		return result
	
	@staticmethod
	def getCountCompleteCommentsFromUserIdAndAssignmentId (userId, assignmentId):
		sql = text ("SELECT COUNT(id) FROM comment WHERE user_id='" + str(userId) + "' AND assignment_id='" + str(assignmentId) + "' AND pending=0")
		result = db.engine.execute(sql)
		names = []
		for row in result: names.append(row)
		return names
	
	@staticmethod
	def deleteCommentsFromAssignmentId (assignmentId):
		sql = text ('DELETE FROM comment WHERE assignment_id=' + '"' + str(assignmentId) + '"')
		result = db.engine.execute(sql)
		return result
	


class Assignment(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	title = db.Column(db.String(140))
	description = db.Column(db.String(280))
	due_date = db.Column(db.Date)
	created_by_id = db.Column(db.Integer)
	target_course = db.Column(db.String(120))
	timestamp = db.Column(db.DateTime, index=True, default=datetime.now)
	peer_review_form = db.Column(db.String(120))
	
	def __repr__(self):
		return '<Assignment {}>'.format(self.title)
	
	@staticmethod
	def deleteAssignmentFromId (assignmentId):
		sql = text ('DELETE FROM assignment WHERE id=' + '"' + str(assignmentId) + '"')
		result = db.engine.execute(sql)
		return result

	@staticmethod
	def getUsersUploadedAssignmentsFromAssignmentId (assignmentId, userId):
		sql = text ('SELECT upload.id FROM assignment INNER JOIN upload ON upload.assignment_id=assignment.id WHERE assignment.id=' + '"' + str(assignmentId) + '" AND user_id=' + str(userId))
		result = db.engine.execute(sql)
		if result == False:
			return False
		filename = []
		for row in result: filename.append(row)
		return filename
	
	@staticmethod
	def getPeerReviewFormFromAssignmentId (assignmentId):
		sql = text ('SELECT peer_review_form FROM assignment WHERE assignment.id=' + '"' + str(assignmentId) + '"')
		result = db.engine.execute(sql)
		if result == False:
			return False
		filename = []
		for row in result: filename.append(row)
		return filename
	


class PeerReviewForm(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	title = db.Column(db.String(140))
	description = db.Column(db.String(280))
	serialisedFormData = db.Column(db.String(280))
	created_by_id = db.Column(db.Integer)
	timestamp = db.Column(db.DateTime, index=True, default=datetime.now)
	
	def __repr__(self):
		return '<PeerReviewForm {}>'.format(self.title)
	