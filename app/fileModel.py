from app import workUpApp
from flask import send_from_directory
import os

# SQL for DB operations
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

# Write a file upload event to db
def writeUploadEvent(originalFilename, randomFilename, userId):
	# Update SQL after file has saved
	post = Post(original_filename = originalFilename, filename = randomFilename, user_id = userId)
	db.session.add(post)
	db.session.commit()