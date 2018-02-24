from app import workUpApp

from flask import render_template, request, Response, make_response, send_file, redirect, url_for, send_from_directory, flash, abort
from flask_httpauth import HTTPBasicAuth
from random import randint
from werkzeug import secure_filename
import glob, os

import upDownTools
from app.login import LoginForm

# App security for stageing server
auth = HTTPBasicAuth()

@auth.get_password
def get_pw(username):
    if username in workUpApp.config['USERS']:
        return workUpApp.config['USERS'].get(username)
    return None


# Log-in page
@workUpApp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        flash('Login requested for user {}, remember_me={}'.format(
            form.username.data, form.remember_me.data))
        return redirect(url_for('uploadFile'))
    return render_template('login.html', form=form)

# Choose a random file from uploads folder and send it out for download
@workUpApp.route('/downloadPeerFile', methods=['POST'])
def downloadRandomFile():	
   uploadedFiles = (os.listdir(workUpApp.config['UPLOAD_FOLDER']))
   numberOfFiles = int (upDownTools.getNumberOfFiles())
   randomNumber = (randint(0,numberOfFiles - 1))
   randomFile = os.path.join (workUpApp.config['UPLOAD_LOCATION'], uploadedFiles[randomNumber])
   return send_file(randomFile, as_attachment=True)


# Sends out a file for download
# Input: filename (must be in upload folder)
@workUpApp.route('/uploaded/<filename>')
def uploadedFile(filename):
	return render_template ('fileUploaded.html')


# Main entrance to the app
@workUpApp.route('/', methods=['GET', 'POST'])
def index():
	return redirect(url_for('uploadFile'))


# Upload form
@workUpApp.route('/upload', methods=['GET', 'POST'])
@auth.login_required
def uploadFile():
	# If the form has been filled out and posted:
	if request.method == 'POST':
		# Check if the post request has the file part
		if 'file' not in request.files:
			flash('No file uploaded.')
			return redirect(request.url)
		file = request.files['file']
		if file.filename == '':
			flash('Please rename the file.')
			return redirect(request.url)
		if file and upDownTools.allowedFile(file.filename):
			filename = secure_filename(file.filename)
			file.save(os.path.join(workUpApp.config['UPLOAD_FOLDER'], filename))
			return redirect(url_for('uploadedFile',filename=filename))
	else:
		flash('Hello, ' + str(auth.username()) + '!')
		return render_template('fileUpload.html')


# Access file stats
@workUpApp.route("/fileStats")
@auth.login_required
def fileStats():
	if (str(auth.username()) in workUpApp.config['ADMIN_USERS'] and workUpApp.config['USERS']):
		printOutput = 'There are ' + str(upDownTools.getNumberOfFiles()) +" files in the folder: "
		uploadedFiles = (glob.glob(workUpApp.config['UPLOAD_FOLDER'] + '/*'))
		return render_template('fileStats.html', numberOfFiles = str(upDownTools.getNumberOfFiles()), uploadedFileNamesArray = uploadedFiles)
	abort(403)
	return None


