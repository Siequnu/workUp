from app import workUpApp

from flask import render_template, session, request, Response, make_response, send_file, redirect, url_for, send_from_directory, flash, abort
from random import randint
import glob, os
import uuid, datetime

# SQL
from flask_login import current_user, login_user
from app.models import User, Post, Download, Comment, Assignment, Class
from flask_login import logout_user
from flask_login import login_required
from werkzeug.urls import url_parse
from app import db
from app.forms import RegistrationForm, AssignmentCreationForm, LoginForm, ClassCreationForm

# Personal classes
import fileModel

@workUpApp.before_request
def before_request():
	if current_user.is_authenticated:
		current_user.last_seen = datetime.datetime.now()
		db.session.commit()

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
		if form.signUpCode.data in workUpApp.config['SIGNUP_CODES']:
			user = User(username=form.username.data, email=form.email.data, studentnumber=form.studentNumber.data, class_id=form.classId.data)
			user.set_password(form.password.data)
			db.session.add(user)
			db.session.commit()
			flash('Congratulations, you are now a registered user!')
			return redirect(url_for('login'))
		else:
			flash("Please ask your tutor for sign-up instructions.")
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
	# Get an array of filenames not belonging to current user
	filesNotFromUser = Post.getPossibleDownloadsNotFromUser(current_user.id)
	numberOfFiles = len(filesNotFromUser)
	if numberOfFiles == 0:
		flash('There are no files currently available for download. Please contact your tutor for advice.')
		return redirect(url_for('index'))
	randomNumber = (randint(0,(numberOfFiles-1)))
	filename = filesNotFromUser[randomNumber]
	randomFile = os.path.join (workUpApp.config['UPLOAD_FOLDER'], filename)
	
	# Send SQL data to database
	download = Download(filename=filename, user_id = current_user.id)
	db.session.add(download)
	db.session.commit()
	
	# Update comments table with pending commment
	postId = Post.getPostIdFromFilename(filename)
	pending = 1
	commentPending = Comment(user_id = int(current_user.id), fileid = int(postId[0]), pending = True)
	db.session.add(commentPending)
	db.session.commit()

	return send_file(randomFile, as_attachment=True)


# Sends out a file for download
# Input: filename (must be in upload folder)
@workUpApp.route('/uploaded/<filename>')
@login_required
def uploadedFile(filename):
	return render_template ('fileUploaded.html')


# Main entrance to the app
@workUpApp.route('/', methods=['GET', 'POST'])
def index():
	if current_user.is_authenticated:
		if current_user.username not in workUpApp.config['ADMIN_USERS']:
			# Get number of uploads
			numberOfUploads = str(Post.getPostCountFromUserId(current_user.id))
		
			# Get total assignments assigned to user's class
			classId = User.getUserClassFromId(current_user.id)
			if (classId[0] == None):
				# User isn't part of a class - doesn't therefore have any assignments
				pass #! todo
			
			# Get assignments due for this user
			assignmentsInfo = Assignment.getAssignmentsFromClassId (str(classId[0]))
			assignmentsForThisUser = []
			for assignment in assignmentsInfo:
				assignmentId = str(assignment[0])
				assignmentsForThisUser.append(assignmentId)
			
			# Check if user has uploaded each assignment
			completedAssignments = 0
			for assignmentId in assignmentsForThisUser:
				userUploadedAssignmentId = Assignment.getUsersUploadedAssignmentsFromAssignmentId (assignmentId, current_user.id)
				if userUploadedAssignmentId:
					completedAssignments += 1
			
			# Set value of progress bar
			if (len(assignmentsForThisUser) != 0):
				progressBarPercentage = int(float(completedAssignments)/float(len(assignmentsForThisUser)) * 100)
			else:
				progressBarPercentage = 100
		
			# Get the pending status of comments
			commentCount = Comment.getPendingStatusFromUserId (current_user.id)
			if commentCount[0] > 0:
				userMustReturnPeerReview = True
			else:
				userMustReturnPeerReview = False
			return render_template('index.html', numberOfUploads = numberOfUploads, progressBarPercentage = progressBarPercentage)
		else:
			return render_template('index.html', admin = True)
	
	return render_template('index.html')


# Upload form, or upload specific file
@workUpApp.route('/upload/<assignmentId>',methods=['GET', 'POST'])
@login_required
def uploadFile(assignmentId = False):
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
		if file and fileModel.allowedFile(file.filename):
			if (assignmentId):
				fileModel.saveFile(file, assignmentId)
			else:
				fileModel.saveFile(file)
			originalFilename = fileModel.getSecureFilename(file.filename)
			return redirect(url_for('uploadedFile',filename=originalFilename))
	else:
		return render_template('fileUpload.html')


# Access file stats
@workUpApp.route("/fileStats")
@login_required
def fileStats():
	import fileStatsModel
	if current_user.username in workUpApp.config['ADMIN_USERS']:
		# Get total list of uploaded files from all users
		templatePackages = {}
		templatePackages['uploadedFiles'] = fileStatsModel.getAllUploadedPostsWithFilenameAndUsername()
		templatePackages['uploadedPostCount'] = str(fileStatsModel.getAllUploadedPostsCount())
		templatePackages['uploadFolderPath'] = workUpApp.config['UPLOAD_FOLDER']
		templatePackages['admin'] = True
		return render_template('fileStats.html', templatePackages = templatePackages)
	elif current_user.is_authenticated:
		templatePackages = {}
		templatePackages['cleanDict'] = fileStatsModel.getPostInfoFromUserId (current_user.id)
		return render_template('fileStats.html', templatePackages = templatePackages)
	abort(403)

# View peer review comments
@workUpApp.route("/comments/<fileid>")
def viewComments(fileid):
	post = Post.getPostOriginalFilenameFromPostId(fileid)
	postTitle = post[0]
	posts = [
		{'author': 'user', 'body': 'Test post #1'},
		{'author': 'user', 'body': 'Test post #2'}
	]
	return render_template('comments.html', posts= posts, postTitle = postTitle)


# Admin page to set new assignment
@workUpApp.route("/createassignment", methods=['GET', 'POST'])
@login_required
def createAssignment():
	if current_user.is_authenticated:
		if current_user.username in workUpApp.config['ADMIN_USERS']:
			form = AssignmentCreationForm()
			if form.validate_on_submit():
				assignment = Assignment(title=form.title.data, description=form.description.data, due_date=form.due_date.data,
									target_course=form.target_course.data, created_by_id=current_user.id)
				db.session.add(assignment)
				db.session.commit()
				flash('Assignment successfully created!')
				return redirect(url_for('index'))
			return render_template('createassignment.html', title='Create Assignment', form=form)
		
		
# View created assignments status
@workUpApp.route("/viewassignments")
@login_required
def viewAssignments():
	import assignmentsModel
	if current_user.username in workUpApp.config['ADMIN_USERS']:
		# Get admin view with all assignments
		assignments = assignmentsModel.getAllAssignments()
		# [(1, u'title', u'descrip', u'2018-03-02 00:00:00.000000', 1, u'30640192-1', u'2018-02-28 13:05:59.287555')]
		return render_template('viewassignments.html', assignmentsArray = assignments, admin = True)
	elif current_user.is_authenticated:
		# Get user class
		classId = assignmentsModel.getUserClassFromId(current_user.id)
		if (classId[0] == None):
			flash('You are not part of any class and can not see any assignments.')
			return render_template('viewassignments.html') # User isn't part of any class - display no assignments
		else:
			# Get assignments for this user
			cleanAssignmentsArray = assignmentsModel.getUserAssignmentInformation (current_user.id)
			return render_template('viewassignments.html', assignmentsArray = cleanAssignmentsArray)
	abort (403)
	
# View created assignments status
@workUpApp.route("/deleteassignment/<assignmentId>")
@login_required
def deleteAssignment(assignmentId):
	import assignmentsModel
	if current_user.username in workUpApp.config['ADMIN_USERS']:
		assignmentsModel.deleteAssignmentFromId(assignmentId)
		flash('Assignment ' + str(assignmentId) + ' has been deleted.')
		return redirect(url_for('viewAssignments'))	
		
	abort (403)


# Admin page to set new class
@workUpApp.route("/createclass", methods=['GET', 'POST'])
@login_required
def createClass():
	if current_user.is_authenticated:
		if current_user.username in workUpApp.config['ADMIN_USERS']:
			form = ClassCreationForm()
			if form.validate_on_submit():
				newClass = Class(class_number=form.classNumber.data, class_label=form.classLabel.data, class_term=form.classTerm.data, class_year = form.classYear.data)
				db.session.add(newClass)
				db.session.commit()
				flash('Class successfully created!')
				return redirect(url_for('index'))
			return render_template('createclass.html', title='Create new class', form=form)
