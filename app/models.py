from datetime import datetime
from app import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import login
from sqlalchemy import text

@login.user_loader
def load_user(id):
	return User.query.get(int(id))

def selectFromDb (columnsArray, fromTable, conditionsArray = False):
	# Assemble SQL query from input variables
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
	def getAllTurmas ():
		sql = text ('SELECT * FROM turma')
		result = db.engine.execute(sql)
		turmas = []
		for turmaInfo in result:
			turmas.append(turmaInfo)
		return turmas

	@staticmethod
	def getTurmaChoiceListForForm ():
		allTurmas = Turma.getAllTurmas ()
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

	def __repr__(self):
		return '<User {}>'.format(self.username)
	
	def set_password(self, password):
		self.password_hash = generate_password_hash(password)

	def check_password(self, password):
		return check_password_hash(self.password_hash, password)
	
	@staticmethod
	def getUserTurmaFromId (userId):
		sql = text('SELECT turma_id FROM user WHERE id=' + str(userId))
		result = db.engine.execute(sql)
		turmaId = []
		for row in result: turmaId.append(row[0])
		return turmaId


class Post(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	original_filename = db.Column(db.String(140))
	filename = db.Column(db.String(140))
	timestamp = db.Column(db.DateTime, index=True, default=datetime.now)
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
	assignment_id = db.Column(db.Integer)
	
	def __repr__(self):
		return '<Post {}>'.format(self.filename)		
	
	@staticmethod
	def getAllUploadedPostsCount ():
		sql = text('SELECT COUNT(id) FROM post')
		result = db.engine.execute(sql)
		names = []
		for row in result: names.append(row[0])
		return names
	
	@staticmethod
	def getAllUploadedPostsWithFilenameAndUsername ():
		sql = text('SELECT post.original_filename, user.username, post.timestamp FROM post INNER JOIN user ON user.id=post.user_id;')
		result = db.engine.execute(sql)
		names = []
		for row in result: names.append(row)
		return names
	
	@staticmethod
	def getPostCountFromUserId (userId):
		return len(Post.query.filter_by(user_id=userId).all())
	
	@staticmethod
	def getPossibleDownloadsNotFromUser (userId):
		sql = text ('SELECT filename FROM post WHERE user_id!=' + str(userId))
		result = db.engine.execute(sql)
		filenames = []
		for row in result: filenames.append(row[0])
		return filenames
	
	@staticmethod
	def getPossibleDownloadsNotFromUserForThisAssignment (userId, assignmentId, previousDownloadFileId = False):
		if previousDownloadFileId:
			sql = text ('SELECT filename FROM post WHERE user_id!=' + str(userId) + ' AND assignment_id=' + str(assignmentId) + ' AND id!=' + str(previousDownloadFileId))
		else:
			sql = text ('SELECT filename FROM post WHERE user_id!=' + str(userId) + ' AND assignment_id=' + str(assignmentId))
		result = db.engine.execute(sql)
		filenames = []
		for row in result: filenames.append(row[0])
		return filenames
	
	@staticmethod
	def getPostOriginalFilenamesFromUserId (userId):
		sql = text ('SELECT original_filename FROM post WHERE user_id=' + str(userId))
		result = db.engine.execute(sql)
		names = []
		for row in result: names.append(row[0])
		return names
	
	@staticmethod
	def getPostInfoFromUserId (userId):
		sql = text ('SELECT original_filename, timestamp, filename, id FROM post WHERE user_id=' + str(userId))
		result = db.engine.execute(sql)
		names = []
		for row in result: names.append(row)
		return names
	
	@staticmethod
	def getPostIdFromFilename (filename):
		sql = text ('SELECT id FROM post WHERE filename=' + '"' + str(filename) + '"')
		result = db.engine.execute(sql)
		names = []
		for row in result: names.append(row[0])
		return names
	
	@staticmethod
	def getPostFilenameFromPostId (postId):
		sql = text ('SELECT filename FROM post WHERE id=' + '"' + str(postId) + '"')
		result = db.engine.execute(sql)
		names = []
		for row in result: names.append(row[0])
		return names
	
	@staticmethod
	def deletePostsFromAssignmentId (assignmentId):
		sql = text ('DELETE FROM post WHERE assignment_id=' + '"' + str(assignmentId) + '"')
		result = db.engine.execute(sql)
		return result

	
class Download(db.Model):
	
	id = db.Column(db.Integer, primary_key=True)
	filename = db.Column(db.String(140))
	timestamp = db.Column(db.DateTime, index=True, default=datetime.now)
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
	
	def __repr__(self):
		return '<Post {}>'.format(self.filename)
	
	@staticmethod
	def getDownloadCountFromFilename (filename):
		sql = text ('SELECT COUNT(id) FROM download WHERE filename=' + '"' + str(filename) + '"')
		result = db.engine.execute(sql)
		count = []
		for row in result: count.append(row[0])
		return count
	

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
		sql = text ('UPDATE comment SET pending=0, comment="' + str(peerReviewContents) + '" WHERE id="' + str(commentId) + '"')
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
	def getCommentContentFromAssignmentIdAndUserId (assignmentId, userId):
		sql = text ("SELECT comment FROM comment WHERE assignment_id='" + str(assignmentId) + "' AND user_id='" + str(userId) + "'")
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
	def getAssignmentDueDateFromId (assignmentId):
		sql = text ('SELECT due_date FROM assignment WHERE id=' + '"' + str(assignmentId) + '"')
		result = db.engine.execute(sql)
		dueDate = []
		for row in result: dueDate.append(row)
		return dueDate
	
	@staticmethod
	def getAllAssignments ():
		sql = text ('SELECT * FROM assignment')
		result = db.engine.execute(sql)
		assignments = []
		for row in result: assignments.append(row)
		return assignments
	
	@staticmethod
	def getAssignmentsFromTurmaId (turmaId):
		sql = text ('SELECT * FROM assignment WHERE target_course=' + '"' + str(turmaId) + '"')
		result = db.engine.execute(sql)
		assignments = []
		for row in result: assignments.append(row)
		return assignments
	
	@staticmethod
	def getAssignmentPeerReviewFormFromAssignmentId (assignmentId):
		sql = text ('SELECT peer_review_form FROM assignment WHERE id=' + '"' + str(assignmentId) + '"')
		result = db.engine.execute(sql)
		assignments = []
		for row in result: assignments.append(row)
		return assignments

	@staticmethod
	def getUsersUploadedAssignmentsFromAssignmentId (assignmentId, userId):
		sql = text ('SELECT post.id FROM assignment INNER JOIN post ON post.assignment_id=assignment.id WHERE assignment.id=' + '"' + str(assignmentId) + '" AND user_id=' + str(userId))
		result = db.engine.execute(sql)
		if result == False:
			return False
		filename = []
		for row in result: filename.append(row)
		return filename
	