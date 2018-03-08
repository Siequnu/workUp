from app import workUpApp

from flask import render_template, session, request, Response, make_response, send_file, redirect, url_for, send_from_directory, flash, abort
from random import randint
import glob, os
import uuid, datetime
import json, pickle

# SQL
from flask_login import current_user, login_user
from app.models import Turma, User, Post, Download, Comment, Assignment
from app import db
db.create_all()
db.session.commit()

from flask_login import logout_user
from flask_login import login_required
from werkzeug.urls import url_parse


from app.forms import LoginForm, RegistrationForm, AdminRegistrationForm, AssignmentCreationForm, TurmaCreationForm, PeerReviewForm, PeerReviewFormTwo

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
			user = User(username=form.username.data, email=form.email.data, studentnumber=form.studentNumber.data, turma_id=form.turmaId.data)
			user.set_password(form.password.data)
			db.session.add(user)
			db.session.commit()
			flash('Congratulations, you are now a registered user!')
			return redirect(url_for('login'))
		else:
			flash("Please ask your tutor for sign-up instructions.")
			return redirect(url_for('login'))
	return render_template('register.html', title='Register', form=form)

# Registration
@workUpApp.route('/registeradmin', methods=['GET', 'POST'])
def registerAdmin():
	if current_user.is_authenticated:
		return redirect(url_for('index'))
	form = AdminRegistrationForm()
	if form.validate_on_submit():
		if form.signUpCode.data in workUpApp.config['SIGNUP_CODES']:
			user = User(username=form.username.data, email=form.email.data)
			user.set_password(form.password.data)
			db.session.add(user)
			db.session.commit()
			flash('Congratulations, you are now a registered administrator!')
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


# Access file stats
@workUpApp.route("/downloadFile")
@workUpApp.route("/downloadFile/<assignmentId>")
@login_required
def downloadFile(assignmentId = False):
	import assignmentsModel
	assignmentIsOver = assignmentsModel.checkIfAssignmentIsOver (assignmentId)
	if assignmentIsOver == True:
		return render_template('downloadFile.html', assignmentId = assignmentId)
	else:
		# If the assignment hasn't closed yet, flash message to wait until after deadline
		flash ("The assignment hasn't closed yet. Please wait until the deadline is over, then try again to download a work for peer review.")
		return redirect (url_for('viewAssignments'))
		
	

# Choose a random file from uploads folder and send it out for download
@workUpApp.route('/downloadPeerFile/<assignmentId>', methods=['POST'])
@login_required
def downloadRandomFile(assignmentId):
	# Check if user has any previous downloads with pending peer reviews
	pendingAssignments = Comment.getPendingStatusFromUserIdAndAssignmentId (current_user.id, assignmentId)
	if len(pendingAssignments) > 0:
		# User has a pending assignment, send them the same file as before
		alreadyDownloadedAndPendingReviewFileId = pendingAssignments[0][1]
		flash('You have a peer review that you have not yet completed. You have redownloaded the same file.')
		# Get filename of the post from Id
		filenameToDownload = Post.getPostFilenameFromPostId (alreadyDownloadedAndPendingReviewFileId)
		
		filePath = os.path.join (workUpApp.config['UPLOAD_FOLDER'], filenameToDownload[0])
		
		# Send SQL data to database
		download = Download(filename=filenameToDownload[0], user_id = current_user.id)
		db.session.add(download)
		db.session.commit()
		
		return send_file(filePath, as_attachment=True)
	
	# Make sure not to give the same file to the same peer reviewer twice
	# Get comments from the user
	completedCommentsIdsAndFileId = Comment.getCommentIdsAndFileIdFromAssignmentIdAndUserId (assignmentId, current_user.id)
	if completedCommentsIdsAndFileId == []:
		filesNotFromUser = Post.getPossibleDownloadsNotFromUserForThisAssignment (current_user.id, assignmentId)
	else:
		# Get an array of filenames not belonging to current user
		previousDownloadFileId = completedCommentsIdsAndFileId[0][1]
		filesNotFromUser = Post.getPossibleDownloadsNotFromUserForThisAssignment (current_user.id, assignmentId, previousDownloadFileId)
	
	numberOfFiles = len(filesNotFromUser)
	if numberOfFiles == 0:
		flash('There are no files currently available for download. Please check back soon.')
		return redirect(url_for('viewAssignments'))
	randomNumber = (randint(0,(numberOfFiles-1)))
	filename = filesNotFromUser[randomNumber]
	randomFile = os.path.join (workUpApp.config['UPLOAD_FOLDER'], filename)
	
	# Send SQL data to database
	download = Download(filename=filename, user_id = current_user.id)
	db.session.add(download)
	db.session.commit()
	
	# Update comments table with pending commment
	postId = Post.getPostIdFromFilename(filename)
	commentPending = Comment(user_id = int(current_user.id), fileid = int(postId[0]), pending = True, assignment_id=assignmentId)
	db.session.add(commentPending)
	db.session.commit()

	return send_file(randomFile, as_attachment=True)


# Main entrance to the app
@workUpApp.route('/', methods=['GET', 'POST'])
def index():
	if current_user.is_authenticated:
		if current_user.username in workUpApp.config['ADMIN_USERS']:	
			
			return render_template('index.html', admin = True)
		if current_user.username not in workUpApp.config['ADMIN_USERS']:
			# Get number of uploads
			numberOfUploads = str(Post.getPostCountFromUserId(current_user.id))
		
			# Get total assignments assigned to user's class
			turmaId = User.getUserTurmaFromId(current_user.id)
			if (turmaId[0] == None):
				# User isn't part of a class - doesn't therefore have any assignments
				pass #! todo
			
			# Get assignments due for this user
			assignmentsInfo = Assignment.getAssignmentsFromTurmaId (str(turmaId[0]))
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
			'''
			# Get the pending status of comments
			commentCount = Comment.getPendingStatusFromUserId (current_user.id)
			if commentCount[0] > 0:
				userMustReturnPeerReview = True
			else:
				userMustReturnPeerReview = False
				'''
			return render_template('index.html', numberOfUploads = numberOfUploads, progressBarPercentage = progressBarPercentage)
	
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
			flash('File ' + str(originalFilename) + ' successfully uploaded')
			return redirect(url_for('viewAssignments'))
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
									target_course=form.target_course.data, created_by_id=current_user.id, peer_review_form=form.peer_review_form.data)
				db.session.add(assignment)
				db.session.commit()
				flash('Assignment successfully created!')
				return redirect(url_for('viewAssignments'))
			return render_template('createassignment.html', title='Create Assignment', form=form)
		
		
# View created assignments status
@workUpApp.route("/viewassignments")
@login_required
def viewAssignments():
	import assignmentsModel
	if current_user.username in workUpApp.config['ADMIN_USERS']:
		# Get admin view with all assignments
		cleanAssignmentsArray = assignmentsModel.getAllAssignments()
		return render_template('viewassignments.html', assignmentsArray = cleanAssignmentsArray, admin = True)
	elif current_user.is_authenticated:
		# Get user class
		turmaId = assignmentsModel.getUserTurmaFromId(current_user.id)
		if (turmaId[0] == None):
			flash('You are not part of any class and can not see any assignments. Ask your tutor for help to join a class.')
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
			form = TurmaCreationForm()
			if form.validate_on_submit():
				newTurma = Turma(turma_number=form.turmaNumber.data, turma_label=form.turmaLabel.data, turma_term=form.turmaTerm.data,
								 turma_year = form.turmaYear.data)
				db.session.add(newTurma)
				db.session.commit()
				flash('Class successfully created!')
				return redirect(url_for('classAdmin'))
			return render_template('createclass.html', title='Create new class', form=form)


# Admin page to view classes
@workUpApp.route("/classadmin")
@login_required
def classAdmin():
	if current_user.is_authenticated:
		if current_user.username in workUpApp.config['ADMIN_USERS']:
			return render_template('classadmin.html', title='Class admin', classesArray = Turma.getAllTurmas())
	abort (403)
		
# Delete a class
@workUpApp.route("/deleteclass/<turmaId>")
@login_required
def deleteClass(turmaId):
	if current_user.username in workUpApp.config['ADMIN_USERS']:
		Turma.deleteClassFromId(turmaId)
		flash('Class ' + str(turmaId) + ' has been deleted.')
		return redirect(url_for('classAdmin'))		
	abort (403)


# Peer review feedback form
@workUpApp.route("/peerreviewform/<assignmentId>", methods=['GET', 'POST'])
@workUpApp.route("/peerreviewform", methods=['GET', 'POST'])
@login_required
def createPeerReview(assignmentId = False):
	form = PeerReviewFormTwo()
	if form.validate_on_submit():
		# Serialise the form contents
		formFields = {}
		for fieldTitle, fieldContents in form.data.items():
			formFields[fieldTitle] = fieldContents
		# Clean the csrf_token and submit fields
		del formFields['csrf_token']
		del formFields['submit']
		formContents = pickle.dumps(formFields)
		
		# Check if user has any previous downloads with pending peer reviews
		pendingAssignments = Comment.getPendingStatusFromUserIdAndAssignmentId (current_user.id, assignmentId)
		if len(pendingAssignments) > 0:
			# User has a pending peer review - update the empty comment field with the contents of this form and remove pending status
			pendingCommentId = pendingAssignments[0][0]
			updateComment = Comment.updatePendingCommentWithComment(pendingCommentId, formContents)
		
		# The database is now updated with the comment - check the total completed comments
		completedComments = Comment.getCountCompleteCommentsFromUserIdAndAssignmentId (current_user.id, assignmentId)
		if completedComments[0][0] == 1:
			# This is the first peer review, submit
			flash('Peer review 1 submitted succesfully!')
		elif completedComments[0][0] == 2:
			# This is the second peer review, submit
			flash('Peer review 2 submitted succesfully!')
		return redirect(url_for('viewAssignments'))
	return render_template('peerreviewform.html', title='Submit a peer review', form=form)

# View a completed and populated peer review form
@workUpApp.route("/viewPeerReview/<assignmentId>/<peerReviewNumber>", methods=['GET', 'POST'])
@login_required
def viewPeerReview(assignmentId, peerReviewNumber):
	# Get the form from the assignmentId
	#peerFormName = Assignment.getAssignmentPeerReviewFormFromAssignmentId (assignmentId)
	
	# Get the first or second peer review - these will be in created order in the DB
	comments = Comment.getCommentContentFromAssignmentIdAndUserId (assignmentId, current_user.id)
	if int(peerReviewNumber) == 1:
		unpackedComments = pickle.loads(comments[0][0])
	elif int(peerReviewNumber) == 2:
		unpackedComments = pickle.loads(comments[1][0])
	# Populate the form
	form = PeerReviewFormTwo(**unpackedComments)
	# Delete submit button
	del form.submit
	flash('You can not edit this peer review as it has already been submitted.')
	return render_template('peerreviewform.html', title='View a peer review', form=form)

