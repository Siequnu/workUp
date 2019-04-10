from app import db, models
from flask import send_from_directory, current_app
from werkzeug import secure_filename
import os
import uuid, datetime

# SQL for DB operations
from flask_login import current_user
from app.models import User, Upload, Download


def get_all_uploads_from_assignment_id (assignment_id):	
	return db.session.query(
		Upload, User).join(
		User).filter(
		Upload.assignment_id == assignment_id).all()	


def getAllUploadsWithFilenameAndUsername ():
		return Upload.getAllUploadsWithFilenameAndUsername()
	

def getAllUploadsCount():
		count = models.selectFromDb (['id'], 'upload', conditionsArray = False, count = True)
		return count[0][0]


def getUploadCountFromCurrentUserId ():
	conditionsArray = []
	conditionsArray.append (str('user_id="' + str(current_user.id) + '"'))
	count = True
	numberOfUploads = models.selectFromDb(['id'], 'upload', conditionsArray, count)
	return numberOfUploads[0][0]


def getPostInfoFromUserId (userId):
	conditions = []
	conditions.append(str('user_id="' + str(userId) + '"'))
	uploadInfo = models.selectFromDb (['id', 'filename', 'timestamp', 'original_filename'], 'upload', conditions)
	cleanDict = {}
	for info in uploadInfo:
		# Get upload time
		datetime = info[2] #2018-02-25 21:50:13.750276
		splitDatetime = str.split(str(datetime)) #['2018-02-25', '21:50:13.750276']
		date = splitDatetime[0]
		timeSplit = str.split(splitDatetime[1], ':') #['21', '50', '13.750276']
		uploadTime = str(timeSplit[0]) + ':' + str(timeSplit[1])
		uploadDateAndtime = date + ' ' + uploadTime
		
		# Get completed comment count from file ID
		fileId = models.selectFromDb(['id'], 'upload', [(str('filename="' + str(info[1]) + '"'))])
		conditions = []
		conditions.append(''.join(('fileid=', str(fileId[0][0]))))
		conditions.append('pending=0')
		peerReviewCount = models.selectFromDb(['id'], 'comment', conditions)
		
		# Add arrayed information to a new dictionary entry
		cleanDict[str(info[3])] = [uploadDateAndtime, str(len(peerReviewCount)), str(info[0])]
	return cleanDict


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