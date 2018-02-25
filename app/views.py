from app import workUpApp

from flask import render_template, session, request, Response, make_response, send_file, redirect, url_for, send_from_directory, flash, abort
from random import randint
from werkzeug import secure_filename
import glob, os
import uuid, datetime # File saving operations, can be moved to upDownTools (rename fileUtils)

## SQL
from flask_login import current_user, login_user
from app.models import User, Post, Download
from flask_login import logout_user
from flask_login import login_required
from werkzeug.urls import url_parse
from app import db
from app.forms import RegistrationForm


# Personal classes
import upDownTools
from app.forms import LoginForm

# Log-out page
@workUpApp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

# Registration
@workUpApp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data, studentnumber=form.studentNumber.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

# Log-in page
@workUpApp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)

# Choose a random file from uploads folder and send it out for download
@workUpApp.route('/downloadPeerFile', methods=['POST'])
@login_required
def downloadRandomFile():	
   uploadedFiles = (os.listdir(workUpApp.config['UPLOAD_FOLDER']))
   numberOfFiles = int (upDownTools.getNumberOfFiles())
   randomNumber = (randint(0,numberOfFiles - 1))
   filename = uploadedFiles[randomNumber]
   randomFile = os.path.join (workUpApp.config['UPLOAD_LOCATION'], filename)
   
   # Send SQL data to database
   download = Download(filename=filename, user_id = current_user.id)
   db.session.add(download)
   db.session.commit()
   return send_file(randomFile, as_attachment=True)


# Sends out a file for download
# Input: filename (must be in upload folder)
@workUpApp.route('/uploaded/<filename>')
def uploadedFile(filename):
	return render_template ('fileUploaded.html')


# Main entrance to the app
@workUpApp.route('/', methods=['GET', 'POST'])
def index():
	return render_template('index.html')


# Upload form
@workUpApp.route('/upload', methods=['GET', 'POST'])
@login_required
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
			originalFilename = secure_filename(file.filename)
			originalFileExtension = upDownTools.getFileExtension(str(originalFilename))
			randomFilename = str(uuid.uuid4()) + '.' + originalFileExtension
			file.save(os.path.join(workUpApp.config['UPLOAD_FOLDER'], randomFilename))
			
			# Update SQL after file has saved
			post = Post(original_filename = originalFilename, filename = randomFilename, user_id = current_user.id,)
			db.session.add(post)
			db.session.commit()
			
			return redirect(url_for('uploadedFile',filename=originalFilename))
	else:
		return render_template('fileUpload.html')


# Access file stats
@workUpApp.route("/fileStats")
@login_required
def fileStats():
	if current_user.username in workUpApp.config['ADMIN_USERS']:
		uploadedFiles = (os.listdir(workUpApp.config['UPLOAD_FOLDER'] ))
		uploadFolderPath = workUpApp.config['UPLOAD_FOLDER']
		return render_template('fileStats.html', numberOfFiles = str(upDownTools.getNumberOfFiles()), uploadedFileNamesArray = uploadedFiles, uploadFolderPath = uploadFolderPath)
	abort(403)
	return None


