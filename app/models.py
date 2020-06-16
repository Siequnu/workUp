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
	try:
		return User.query.filter(User.username==username).one_or_none().is_admin
	except:
		return False

class StatementProject (db.Model):
	__table_args__ = {'sqlite_autoincrement': True}
	id = db.Column(db.Integer, primary_key=True)
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
	title = db.Column(db.String(140))
	timestamp = db.Column(db.DateTime, index=True, default=datetime.now())
	archived = db.Column(db.Boolean, default=False)
	
	def __repr__(self):
		return '<Statement Project {}>'.format(self.id)
	
class StatementUpload (db.Model):
	__table_args__ = {'sqlite_autoincrement': True}
	id = db.Column(db.Integer, primary_key=True)
	project_id = db.Column(db.Integer, db.ForeignKey('statement_project.id'))
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
	original_filename = db.Column(db.String(140))
	filename = db.Column(db.String(140))
	timestamp = db.Column(db.DateTime, index=True, default=datetime.now())
	description = db.Column(db.String(250))
	
	def __repr__(self):
		return '<Statement Upload {}>'.format(self.id)
	
class StatementDownload(db.Model):
	__table_args__ = {'sqlite_autoincrement': True}
	id = db.Column(db.Integer, primary_key=True)
	statement_id = db.Column(db.Integer, db.ForeignKey('statement_upload.id'))
	timestamp = db.Column(db.DateTime, index=True, default=datetime.now())
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
	
	def __repr__(self):
		return '<Statement Download {}>'.format(self.filename)


class ClassLibraryFile (db.Model):
	__table_args__ = {'sqlite_autoincrement': True}
	id = db.Column(db.Integer, primary_key=True)
	turma_id = db.Column(db.Integer, db.ForeignKey('turma.id'))
	library_upload_id = db.Column(db.Integer, db.ForeignKey('library_upload.id'))
	
	def __repr__(self):
		return '<Class Library File {}>'.format(self.id)
	
class LibraryDownload(db.Model):
	__table_args__ = {'sqlite_autoincrement': True}
	id = db.Column(db.Integer, primary_key=True)
	library_upload_id = db.Column(db.Integer, db.ForeignKey('library_upload.id'))
	timestamp = db.Column(db.DateTime, index=True, default=datetime.now())
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
	
	def __repr__(self):
		return '<Download {}>'.format(self.id)

class LibraryUpload (db.Model):
	__table_args__ = {'sqlite_autoincrement': True}
	id = db.Column(db.Integer, primary_key=True)
	original_filename = db.Column(db.String(140))
	filename = db.Column(db.String(140))
	timestamp = db.Column(db.DateTime, index=True, default=datetime.now())
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
	title = db.Column(db.String(140))
	description = db.Column(db.String(500))

	def __repr__(self):
		return '<Library Upload {}>'.format(self.original_filename)

class Turma(db.Model):
	__table_args__ = {'sqlite_autoincrement': True}
	id = db.Column(db.Integer, primary_key=True, index = True)
	turma_number = db.Column(db.String(140))
	turma_label = db.Column(db.String(140))
	turma_term = db.Column(db.String(140))
	turma_year = db.Column(db.Integer)
	lesson_start_time = db.Column(db.Time)
	lesson_end_time = db.Column(db.Time)
	
	def __repr__(self):
		return '<Turma {}>'.format(self.turma_number)

	@staticmethod
	def new_turma_from_form (form):
		new_turma = Turma(turma_number=form.turma_number.data, turma_label=form.turma_label.data,
					turma_term=form.turma_term.data,
					turma_year = form.turma_year.data,
					lesson_start_time = form.lesson_start_time.data,
					lesson_end_time = form.lesson_end_time.data)
		db.session.add(new_turma)
		db.session.commit()


	@staticmethod
	def delete_turma_from_id (turma_id):
		Turma.query.filter(Turma.id==turma_id).delete()
		Assignment.query.filter(Assignment.target_turma_id==turma_id).delete()
		ClassLibraryFile.query.filter(ClassLibraryFile.turma_id==turma_id).delete()
		Enrollment.query.filter(Enrollment.turma_id==turma_id).delete()
		db.session.commit()
	
	
class Enrollment (db.Model):
	__table_args__ = {'sqlite_autoincrement': True}
	id = db.Column(db.Integer, primary_key=True)
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
	turma_id = db.Column(db.Integer, db.ForeignKey('turma.id'))
	
	def __repr__(self):
		return '<Enrollment {}>'.format(self.id)
	

	
class ReferenceUpload (db.Model):
	__table_args__ = {'sqlite_autoincrement': True}
	id = db.Column(db.Integer, primary_key=True)
	form_contents = db.Column(db.String(10000))
	suitability = db.Column(db.String(5000))
	school_information = db.Column(db.String(5000))
	student_id = db.Column(db.Integer, db.ForeignKey('user.id'))
	student_name = db.Column(db.String(50))
	referee_name = db.Column(db.String(50))
	referee_position = db.Column(db.String(200))
	archived = db.Column(db.Boolean, default=False)
	
	def __repr__(self):
		return '<Reference {}>'.format(self.id)
	
class ReferenceVersionUpload (db.Model):
	__table_args__ = {'sqlite_autoincrement': True}
	id = db.Column(db.Integer, primary_key=True)
	original_reference_id = db.Column(db.Integer, db.ForeignKey('reference_upload.id'))
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
	original_filename = db.Column(db.String(140))
	filename = db.Column(db.String(140))
	timestamp = db.Column(db.DateTime, index=True, default=datetime.now())
	description = db.Column(db.String(250))
	
	def __repr__(self):
		return '<Reference Version {}>'.format(self.id)

class ReferenceVersionDownload(db.Model):
	__table_args__ = {'sqlite_autoincrement': True}
	id = db.Column(db.Integer, primary_key=True)
	reference_version_id = db.Column(db.Integer, db.ForeignKey('reference_version_upload.id'))
	timestamp = db.Column(db.DateTime, index=True, default=datetime.now())
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
	
	def __repr__(self):
		return '<Reference Version Download {}>'.format(self.filename)
	

class User(UserMixin, db.Model):
	__table_args__ = {'sqlite_autoincrement': True}
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(64), index=True, unique=True)
	email = db.Column(db.String(120), index=True, unique=True)
	password_hash = db.Column(db.String(128))
	student_number = db.Column(db.String(12))
	last_seen = db.Column(db.DateTime, default=datetime.now())
	registered = db.Column(db.DateTime, default=datetime.now())
	email_confirmed = db.Column(db.Boolean, default=False)
	is_admin = db.Column(db.Boolean, default=False)
	profile_name = db.Column(db.String(200))
	profile_title = db.Column(db.String(200))
	profile_education = db.Column(db.String(200))
	profile_qualification = db.Column(db.String(200))
	profile_text = db.Column(db.String(2000))
	profile_picture = db.Column(db.String(200))


	def __repr__(self):
		return '<User {}>'.format(self.username)
	
	def set_password(self, password):
		self.password_hash = generate_password_hash(password)

	def check_password(self, password):
		return check_password_hash(self.password_hash, password)

	@staticmethod
	def user_email_is_confirmed (username):
		return User.query.filter_by(username=username).first().email_confirmed
	
	@staticmethod
	def give_admin_rights(user_id):
		user = User.query.get(user_id)
		user.is_admin = True
		db.session.commit()
	
	@staticmethod
	def remove_admin_rights(user_id):
		if int(user_id) != 1: # Can't remove original admin
			user = User.query.get(user_id)
			user.is_admin = False
			db.session.commit()
	
	@staticmethod
	def delete_user (user_id):
		if int(user_id) != 1: # Can't remove original admin			
			user = User.query.get(user_id)
			db.session.delete(user)
			db.session.commit()
			return True
		else:
			return False


class Upload(db.Model):
	__table_args__ = {'sqlite_autoincrement': True}
	id = db.Column(db.Integer, primary_key=True)
	original_filename = db.Column(db.String(140))
	filename = db.Column(db.String(140))
	timestamp = db.Column(db.DateTime, default=datetime.now())
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
	assignment_id = db.Column(db.Integer, db.ForeignKey('assignment.id'))
	
	def __repr__(self):
		return '<Upload {}>'.format(self.filename)

	
class Download(db.Model):
	__table_args__ = {'sqlite_autoincrement': True}
	id = db.Column(db.Integer, primary_key=True)
	filename = db.Column(db.String(140))
	timestamp = db.Column(db.DateTime, index=True, default=datetime.now())
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
	
	def __repr__(self):
		return '<Download {}>'.format(self.filename)
	


class Comment(db.Model):
	__table_args__ = {'sqlite_autoincrement': True}
	id = db.Column(db.Integer, primary_key=True)
	comment = db.Column(db.String(5000))
	timestamp = db.Column(db.DateTime, index=True, default=datetime.now())
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
	file_id = db.Column(db.Integer)
	pending = db.Column(db.Boolean)
	assignment_id = db.Column(db.Integer, db.ForeignKey('assignment.id'))
	
	def __repr__(self):
		return '<Comment {}>'.format(self.id)
	
	@staticmethod
	def get_pending_status_from_user_id_and_assignment_id (user_id, assignment_id):
		return Comment.query.filter(
			Comment.user_id == user_id).filter(
			Comment.assignment_id == assignment_id).filter(
			Comment.pending == True).first()
	
	@staticmethod
	def update_pending_comment_with_contents (comment_id, peer_review_contents):
		comment_object= Comment.query.get(comment_id)
		comment_object.comment = peer_review_contents
		comment_object.pending = False
		comment_object.timestamp = datetime.now()
		db.session.commit()
	
	@staticmethod
	def get_completed_peer_reviews_from_user_for_assignment (user_id, assignment_id):
		return Comment.query.filter_by(user_id=user_id).filter_by(assignment_id=assignment_id).filter_by(pending=0).all()


class Assignment(db.Model):
	__table_args__ = {'sqlite_autoincrement': True}
	id = db.Column(db.Integer, primary_key=True)
	title = db.Column(db.String(140))
	description = db.Column(db.String(1500))
	due_date = db.Column(db.Date)
	created_by_id = db.Column(db.Integer, db.ForeignKey('user.id'))
	target_turma_id = db.Column(db.Integer, db.ForeignKey('turma.id'))
	timestamp = db.Column(db.DateTime, index=True, default=datetime.now())
	peer_review_necessary = db.Column(db.Boolean, default=False)
	peer_review_form_id = db.Column(db.Integer, db.ForeignKey('peer_review_form.id'))
	assignment_task_file_id = db.Column(db.Integer, db.ForeignKey('assignment_task_file.id'))
	
	def __repr__(self):
		return '<Assignment {}>'.format(self.title)

class PeerReviewForm(db.Model):
	__table_args__ = {'sqlite_autoincrement': True}
	id = db.Column(db.Integer, primary_key=True)
	title = db.Column(db.String(140))
	description = db.Column(db.String(280))
	serialised_form_data = db.Column(db.String(1000))
	created_by_id = db.Column(db.Integer, db.ForeignKey('user.id'))
	timestamp = db.Column(db.DateTime, index=True, default=datetime.now())
	
	def __repr__(self):
		return '<PeerReviewForm {}>'.format(self.title)
	

class CommentFileUpload(db.Model):
	__table_args__ = {'sqlite_autoincrement': True}
	id = db.Column(db.Integer, primary_key=True)
	original_filename = db.Column(db.String(140))
	filename = db.Column(db.String(140))
	timestamp = db.Column(db.DateTime, default=datetime.now())
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
	comment_id = db.Column(db.Integer, db.ForeignKey('comment.id'))
	
	def __repr__(self):
		return '<Comment File Upload {}>'.format(self.original_filename)
	

class Lesson (db.Model):
	__table_args__ = {'sqlite_autoincrement': True}
	id = db.Column(db.Integer, primary_key=True)
	date = db.Column(db.Date)
	start_time = db.Column(db.Time)
	end_time = db.Column(db.Time)
	turma_id = db.Column(db.Integer, db.ForeignKey('turma.id'))
	
	def __repr__(self):
		return '<Lesson {}>'.format(self.id)
	
class LessonAttendance (db.Model):
	__table_args__ = {'sqlite_autoincrement': True}
	id = db.Column(db.Integer, primary_key=True)
	lesson_id = db.Column(db.Integer, db.ForeignKey('lesson.id'))
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
	timestamp = db.Column(db.DateTime, default=datetime.now())
	
	def __repr__(self):
		return '<Lesson Attendance {}>'.format(self.id)
	


class Inquiry (db.Model):
	__table_args__ = {'sqlite_autoincrement': True}
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(140))
	email = db.Column(db.String(140))
	timestamp = db.Column(db.DateTime, index=True, default=datetime.now())
	message = db.Column(db.String(500))
	
	def save (self):
		db.session.add(self)
		db.session.commit ()

	#¡# Send an email to admin?
	def __repr__(self):
		return '<Inquiry {}>'.format(self.id)