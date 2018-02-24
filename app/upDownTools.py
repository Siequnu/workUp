from app import app
from flask import send_from_directory
import os

# Check filename and extension permissibility
def allowedFile(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

# Return the number of files in the upload folder
def getNumberOfFiles():
	return (len (os.listdir(app.config['UPLOAD_FOLDER'])) - 1 )

# Send out specific file for download
def downloadFile(filename):
	return send_from_directory(app.config['UPLOAD_FOLDER'], filename)