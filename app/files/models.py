from app import db, models
from flask import send_from_directory, current_app
from werkzeug import secure_filename
import os
import uuid, datetime

# SQL for DB operations
from flask_login import current_user
from app.models import User, Upload, Download, Assignment, Comment
from sqlalchemy import func

def get_all_uploads_from_assignment_id (assignment_id):	
	return db.session.query(
		Upload, User).join(User).filter(
		Upload.assignment_id == assignment_id).all()	


def get_uploads_object ():
	return Upload.query.all()
	
def get_all_uploads_count():
	return Upload.query.count()

def add_teacher_comment_to_upload (form_contents, upload_id):
	comment = Comment(comment = form_contents, user_id = current_user.id,
					  file_id = upload_id, pending = False, assignment_id = Upload.query.get(upload_id).assignment_id)
	db.session.add(comment)
	db.session.commit()
	return True

def get_uploaded_file_count_from_user_id (user_id):
	return Upload.query.filter_by(user_id=current_user.id).count()

def get_peer_review_form_from_upload_id (upload_id):
	return db.session.query(
		Assignment).join(
		Upload,Assignment.id==Upload.assignment_id).filter(
		Upload.id == upload_id).first().peer_review_form

# Get all post info and comment count for a user
def get_post_info_from_user_id (user_id):	
	return db.session.query(Upload, func.count(Comment.id)).join(
		Comment, Upload.id==Comment.file_id).group_by(Upload.filename).filter(Upload.user_id==user_id).all()


# Check filename and extension permissibility
def allowedFile(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']


def get_file_extension(filename):
	return filename.rsplit('.', 1)[1].lower()


# Return the number of files in the upload folder
def getNumberOfFiles():
	return (len (os.listdir(current_app.config['UPLOAD_FOLDER'])))


# Send out specific file for download
def download_file(filename):
	return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename)


# Saves a file to uplaods folder, returns secure filename
def save_file (file):
	original_filename = secure_filename(file.filename)
	random_filename = get_random_uuid_filename (original_filename)
	file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], random_filename))
	return random_filename

# Save a file to uploads folder, and update DB
def save_assignment_file (file, assignment_id):
	original_filename = secure_filename(file.filename)
	random_filename = save_file (file)
	
	# Update SQL after file has saved
	upload = Upload(original_filename = original_filename, filename = random_filename, user_id = current_user.id, assignment_id = assignment_id)
	db.session.add(upload)
	db.session.commit()

# Verify a filename is secure with werkzeug library
def get_secure_filename(filename):
	return secure_filename(filename)


# Return randomised filename, keeping the original extension
def get_random_uuid_filename(original_filename):
	original_file_extension = get_file_extension(str(original_filename))
	random_filename = str(uuid.uuid4()) + '.' + original_file_extension
	return random_filename