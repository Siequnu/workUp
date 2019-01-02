from app import workUpApp

from flask import render_template, flash, redirect, url_for, request
from flask_login import current_user

# Login
from flask_login import login_required

# Models
import assignmentsModel
import fileModel
import fileStatsModel



# Access file stats
@workUpApp.route("/fileStats")
@login_required
def fileStats():
	if current_user.username in workUpApp.config['ADMIN_USERS']:
		# Get total list of uploaded files from all users
		templatePackages = {}
		templatePackages['uploadedFiles'] = fileStatsModel.getAllUploadsWithFilenameAndUsername()
		templatePackages['uploadedPostCount'] = str(fileStatsModel.getAllUploadsCount())
		templatePackages['uploadFolderPath'] = workUpApp.config['UPLOAD_FOLDER']
		templatePackages['admin'] = True
		return render_template('fileStats.html', templatePackages = templatePackages)
	elif current_user.is_authenticated:
		templatePackages = {}
		templatePackages['cleanDict'] = fileStatsModel.getPostInfoFromUserId (current_user.id)
		return render_template('fileStats.html', templatePackages = templatePackages)
	abort(403)



# Download a file for peer review
@workUpApp.route("/downloadFile")
@workUpApp.route("/downloadFile/<assignmentId>")
@login_required
def downloadFile(assignmentId = False):
	assignmentIsOver = assignmentsModel.checkIfAssignmentIsOver (assignmentId)
	if assignmentIsOver == True:
		return render_template('downloadFile.html', assignmentId = assignmentId)
	else:
		# If the assignment hasn't closed yet, flash message to wait until after deadline
		flash ("The assignment hasn't closed yet. Please wait until the deadline is over, then try again to download an assignemnt to review.")
		return redirect (url_for('viewAssignments'))
		

	
# Upload form, or upload specific file
@workUpApp.route('/upload/<assignmentId>',methods=['GET', 'POST'])
@login_required
def uploadFile(assignmentId = False):
	# If the form has been filled out and posted:
	if request.method == 'POST':
		if 'file' not in request.files:
			flash('No file uploaded. Please try again or contact your tutor.')
			return redirect(request.url)
		file = request.files['file']
		if file.filename == '':
			flash('The filename is blank. Please rename the file.')
			return redirect(request.url)
		if file and fileModel.allowedFile(file.filename):
			if (assignmentId):
				fileModel.saveFile(file, assignmentId)
			else:
				fileModel.saveFile(file)
			originalFilename = fileModel.getSecureFilename(file.filename)
			flash('Your file ' + str(originalFilename) + ' successfully uploaded')
			return redirect(url_for('viewAssignments'))
		else:
			flash('You can not upload this kind of file.')
			return redirect(url_for('viewAssignments'))
	else:
		return render_template('fileUpload.html')

	