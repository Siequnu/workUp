from app import workUpApp
from flask import send_from_directory
from werkzeug import secure_filename
import os
import uuid, datetime

# SQL for DB operations
from flask_login import current_user
from app.models import User, Post, Download
from app import db

# Check filename and extension permissibility
def allowedFile(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in workUpApp.config['ALLOWED_EXTENSIONS']

def getFileExtension(filename):
	return filename.rsplit('.', 1)[1].lower()

# Return the number of files in the upload folder
def getNumberOfFiles():
	return (len (os.listdir(workUpApp.config['UPLOAD_FOLDER'])))

# Send out specific file for download
def downloadFile(filename):
	return send_from_directory(workUpApp.config['UPLOAD_FOLDER'], filename)

# Save a file to uploads folder, and update DB
def saveFile (file):
	originalFilename = getSecureFilename(file.filename)
	randomFilename = getRandomFilename (originalFilename)
	file.save(os.path.join(workUpApp.config['UPLOAD_FOLDER'], randomFilename))
	
	# Update SQL after file has saved
	writeUploadEvent (originalFilename, randomFilename, userId = current_user.id)

# Verify a filename is secure with werkzeug library
def getSecureFilename(filename):
	return secure_filename(filename)

# Return randomised filename, keeping the original extension
def getRandomFilename(originalFilename):
	originalFileExtension = getFileExtension(str(originalFilename))
	randomFilename = str(uuid.uuid4()) + '.' + originalFileExtension
	return randomFilename

# Write a file upload event to db
def writeUploadEvent(originalFilename, randomFilename, userId):
	# Update SQL after file has saved
	post = Post(original_filename = originalFilename, filename = randomFilename, user_id = userId)
	db.session.add(post)
	db.session.commit()