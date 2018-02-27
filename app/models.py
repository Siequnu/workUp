from datetime import datetime
from app import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import login
from sqlalchemy import text

@login.user_loader
def load_user(id):
    return User.query.get(int(id))
class User(UserMixin, db.Model):
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(64), index=True, unique=True)
	email = db.Column(db.String(120), index=True, unique=True)
	password_hash = db.Column(db.String(128))
	studentnumber = db.Column(db.String(12))
	last_seen = db.Column(db.DateTime, default=datetime.now)
	registered = db.Column(db.DateTime, default=datetime.now)

	def __repr__(self):
		return '<User {}>'.format(self.username)
	
	def set_password(self, password):
		self.password_hash = generate_password_hash(password)

	def check_password(self, password):
		return check_password_hash(self.password_hash, password)

class Post(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	original_filename = db.Column(db.String(140))
	filename = db.Column(db.String(140))
	timestamp = db.Column(db.DateTime, index=True, default=datetime.now)
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
	
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
	def getPostOriginalFilenameFromPostId (postId):
		sql = text ('SELECT original_filename FROM post WHERE id=' + str(postId))
		result = db.engine.execute(sql)
		names = []
		for row in result: names.append(row[0])
		return names

	
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
