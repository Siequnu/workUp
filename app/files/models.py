from app import db, models
from flask import send_from_directory, current_app
from werkzeug import secure_filename
import os, uuid, datetime, arrow

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

def get_file_owner_id (file_id):
	return Upload.query.get(file_id).user_id

def get_peer_reviews_from_upload_id (upload_id):
	return Comment.query.filter_by(file_id=upload_id).filter_by(pending=False).all()

def get_upload_filename_from_upload_id (upload_id):
	return Upload.query.get(upload_id).original_filename

# Get all post info and comment count for a user
def get_post_info_from_user_id (user_id):	
	upload_info = db.session.query(Upload).filter(Upload.user_id==user_id).all()
	upload_array =[]
	for upload in upload_info:
		upload_dict = upload.__dict__ # Convert the SQL Alchemy object into dictionary
		upload_dict['number_of_comments'] = get_received_peer_review_from_upload_id_count(upload_dict['id'])
		formatted_datetime = arrow.get (upload_dict['timestamp'])
		upload_dict['timestamp'] = formatted_datetime.format('YYYY-MM-DD HH:mm:ss')
		upload_array.append(upload_dict)
	return upload_array

def get_received_peer_review_from_upload_id_count (upload_id):
	return Comment.query.filter_by(file_id=upload_id).count()

# Check filename and extension permissibility
def allowed_file_extension(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

def get_file_extension(filename):
	return filename.rsplit('.', 1)[1].lower()

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
	upload = Upload(original_filename = original_filename, filename = random_filename,
					user_id = current_user.id, assignment_id = assignment_id)
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