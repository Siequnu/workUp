from datetime import datetime
from app import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, current_user
from app import login
from sqlalchemy import text, cast, String
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
		columnsArray.reverse()
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
	def new_turma_from_form (form):
		new_turma = Turma(turma_number=form.turmaNumber.data, turma_label=form.turmaLabel.data,
					turma_term=form.turmaTerm.data,
					turma_year = form.turmaYear.data)
		db.session.add(new_turma)
		db.session.commit()

	@staticmethod
	def get_class_list_for_forms ():
		return db.session.query(cast(Turma.id, String(64)), Turma.turma_label).all()
	
	@staticmethod
	def delete_turma_from_id (turma_id):
		Turma.query.filter(Turma.id==turma_id).delete()
		db.session.commit()

class User(UserMixin, db.Model):
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(64), index=True, unique=True)
	email = db.Column(db.String(120), index=True, unique=True)
	password_hash = db.Column(db.String(128))
	student_number = db.Column(db.String(12))
	turma_id = db.Column(db.Integer, db.ForeignKey('turma.id'))
	last_seen = db.Column(db.DateTime, default=datetime.now())
	registered = db.Column(db.DateTime, default=datetime.now())
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
	def get_all_user_info ():
		return User.query.all()
	
	@staticmethod
	def give_admin_rights(user_id):
		sql = text ("UPDATE user SET is_admin=1 WHERE id='" + str(user_id) + "'")
		result = db.engine.execute(sql)
		return result
	
	@staticmethod
	def remove_admin_rights(user_id):
		sql = text ("UPDATE user SET is_admin=0 WHERE id='" + str(user_id) + "'")
		result = db.engine.execute(sql)
		return result
		
		
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
	
	@staticmethod
	def get_user_turma_from_user_id (user_id):
		return User.query.get(user_id).turma_id
	
	
class AssignmentTaskFile(db.Model):
	id = db.Column(db.Integer, primary_key=True, autoincrement=True)
	original_filename = db.Column(db.String(140))
	filename = db.Column(db.String(140))
	timestamp = db.Column(db.DateTime, index=True, default=datetime.now())
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
	
	def __repr__(self):
		return '<Assignment Task File {}>'.format(self.filename)		



class Upload(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	original_filename = db.Column(db.String(140))
	filename = db.Column(db.String(140))
	timestamp = db.Column(db.DateTime, index=True, default=datetime.now())
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
	assignment_id = db.Column(db.Integer, db.ForeignKey('assignment.id'))
	
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

	
	
class Download(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	filename = db.Column(db.String(140))
	timestamp = db.Column(db.DateTime, index=True, default=datetime.now())
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
	
	def __repr__(self):
		return '<Download {}>'.format(self.filename)
	


class Comment(db.Model):
	
	id = db.Column(db.Integer, primary_key=True)
	comment = db.Column(db.String(500))
	timestamp = db.Column(db.DateTime, index=True, default=datetime.now())
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
	file_id = db.Column(db.Integer)
	pending = db.Column(db.Boolean)
	assignment_id = db.Column(db.Integer, db.ForeignKey('assignment.id'))
	
	def __repr__(self):
		return '<Comment {}>'.format(self.comment)
	
	@staticmethod
	def getPendingStatusFromUserIdAndAssignmentId (userId, assignmentId):
		sql = text ('SELECT id, file_id FROM comment WHERE user_id=' + str(userId) + ' AND assignment_id=' + str(assignmentId) + ' AND pending=1')
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
	def get_completed_peer_reviews_from_user_for_assignment (user_id, assignment_id):
		return Comment.query.filter_by(user_id=user_id).filter_by(assignment_id=assignment_id).filter_by(pending=0).all()
	
	@staticmethod
	def getCountCompleteCommentsFromUserIdAndAssignmentId (userId, assignmentId):
		sql = text ("SELECT COUNT(id) FROM comment WHERE user_id='" + str(userId) + "' AND assignment_id='" + str(assignmentId) + "' AND pending=0")
		result = db.engine.execute(sql)
		names = []
		for row in result: names.append(row)
		return names
	


class Assignment(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	title = db.Column(db.String(140))
	description = db.Column(db.String(280))
	due_date = db.Column(db.Date)
	created_by_id = db.Column(db.Integer, db.ForeignKey('user.id'))
	target_turma_id = db.Column(db.Integer, db.ForeignKey('turma.id'))
	timestamp = db.Column(db.DateTime, index=True, default=datetime.now())
	peer_review_necessary = db.Column(db.Boolean, default=False)
	peer_review_form = db.Column(db.String(120)) # Should be peer_review_form_id, and db.ForeignKey
	assignment_task_file_id = db.Column(db.Integer, db.ForeignKey('assignment_task_file.id'))
	
	def __repr__(self):
		return '<Assignment {}>'.format(self.title)
	
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
	serialised_form_data = db.Column(db.String(280))
	created_by_id = db.Column(db.Integer, db.ForeignKey('user.id'))
	timestamp = db.Column(db.DateTime, index=True, default=datetime.now())
	
	def __repr__(self):
		return '<PeerReviewForm {}>'.format(self.title)
	