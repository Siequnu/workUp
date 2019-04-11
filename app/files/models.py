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
		Upload, User).join(
		User).filter(
		Upload.assignment_id == assignment_id).all()	


def getAllUploadsWithFilenameAndUsername ():
	return Upload.getAllUploadsWithFilenameAndUsername()
	

def get_all_uploads_count():
	return Upload.query.count()

def add_teacher_comment_to_upload (form_contents, upload_id):
	comment = Comment(comment = form_contents, user_id = current_user.id,
					  fileid = upload_id, pending = False, assignment_id = Upload.query.get(upload_id).assignment_id)
	db.session.add(comment)
	db.session.commit()
	return True

def getUploadCountFromCurrentUserId ():
	conditionsArray = []
	conditionsArray.append (str('user_id="' + str(current_user.id) + '"'))
	count = True
	numberOfUploads = models.selectFromDb(['id'], 'upload', conditionsArray, count)
	return numberOfUploads[0][0]

def get_peer_review_form_from_upload_id (upload_id):
	info = db.session.query(
		Upload, Assignment).join(
		Assignment, Upload.assignment_id == Assignment.id).filter(Upload.id == upload_id).first()
	return info[1].peer_review_form

# Get all post info and comment count for a user
def get_post_info_from_user_id (user_id):	
	return db.session.query(Upload, func.count(Comment.id)).join(Comment, Upload.id==Comment.fileid).group_by(Upload.filename).filter(Upload.user_id==user_id).all()


# Check filename and extension permissibility
def allowedFile(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']


def getFileExtension(filename):
	return filename.rsplit('.', 1)[1].lower()


# Return the number of files in the upload folder
def getNumberOfFiles():
	return (len (os.listdir(current_app.config['UPLOAD_FOLDER'])))


# Send out specific file for download
def download_file(filename):
	return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename)


# Save a file to uploads folder, and update DB
def saveFile (file, assignmentId = False):
	originalFilename = getSecureFilename(file.filename)
	randomFilename = getRandomFilename (originalFilename)
	file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], randomFilename))
	
	# Update SQL after file has saved
	writeUploadEvent (originalFilename, randomFilename, userId = current_user.id, assignment_id = assignmentId)

# Verify a filename is secure with werkzeug library
def getSecureFilename(filename):
	return secure_filename(filename)


# Return randomised filename, keeping the original extension
def getRandomFilename(originalFilename):
	originalFileExtension = getFileExtension(str(originalFilename))
	randomFilename = str(uuid.uuid4()) + '.' + originalFileExtension
	return randomFilename


# Write a file upload event to db
def writeUploadEvent(originalFilename, randomFilename, userId, assignment_id = False):
	# Update SQL after file has saved
	if assignment_id:
			upload = Upload(original_filename = originalFilename, filename = randomFilename, user_id = userId, assignment_id = assignment_id)
	else:
		upload = Upload(original_filename = originalFilename, filename = randomFilename, user_id = userId)
	db.session.add(upload)
	db.session.commit()