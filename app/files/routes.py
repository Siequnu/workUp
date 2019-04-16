from flask import render_template, flash, redirect, url_for, request, current_app, send_file
from flask_login import current_user

# Login
from flask_login import login_required
from app import db

# Models
import app.assignments.models

from app.files import bp
from app.files import models
from app.models import Comment, Download, Upload, Assignment

from random import randint
import os, datetime, json

# Forms
from app.main.forms import FormModel
from app.assignments.forms_peer_review import *

# Access file stats
@bp.route("/file_stats")
@login_required
def file_stats():
	if current_user.is_authenticated and app.models.is_admin(current_user.username):
		# Get total list of uploaded files from all users
		template_packages = {}
		template_packages['uploads_object'] = models.get_uploads_object()
		template_packages['total_upload_count'] = str(models.get_all_uploads_count())
		template_packages['upload_folder_path'] = current_app.config['UPLOAD_FOLDER']
		template_packages['admin'] = True
		return render_template('files/file_stats_admin.html', template_packages = template_packages)
	elif current_user.is_authenticated:		
		return render_template('files/file_stats.html', comment = Comment, all_post_info = models.get_post_info_from_user_id (current_user.id))
	abort(403)



# Choose a random file from uploads folder and send it out for download
@bp.route('/download_random_file/<assignment_id>', methods=['POST'])
@login_required
def download_random_file(assignment_id):
	# Check if user has any previous downloads with pending peer reviews
	pending_assignments = Comment.getPendingStatusFromUserIdAndAssignmentId (current_user.id, assignment_id)
	print (pending_assignments) # (2, 1) if first assignment, or [] if none left?
	if len(pending_assignments) > 0:
		# User has a pending assignment, send them the same file as before
		already_downloaded_and_pending_review_file_id = pending_assignments[0][1]
		flash('You have a peer review that you have not yet completed. You have redownloaded the same file.')
		# Get filename of the upload from Id
		conditions = []
		conditions.append(str('id="' + str(already_downloaded_and_pending_review_file_id) + '"'))
		filename_to_download = app.models.selectFromDb(['filename'], 'upload', conditions)		
		file_path = os.path.join (current_app.config['UPLOAD_FOLDER'], filename_to_download[0][0])
		# Send SQL data to database
		download = Download(filename=filename_to_download[0][0], user_id = current_user.id)
		db.session.add(download)
		db.session.commit()
		
		return send_file(file_path, as_attachment=True)
	
	# Make sure not to give the same file to the same peer reviewer twice
	# Get list of files the user has already submitted reviews for
	conditions = []
	conditions.append (str('assignment_id="' + str(assignment_id) + '"'))
	conditions.append (str('user_id="' + str(current_user.id) + '"'))
	completed_comments_ids_and_file_id = app.models.selectFromDb(['id', 'file_id'], 'comment', conditions)
	
	if completed_comments_ids_and_file_id == []:
		files_not_from_user = Upload.getPossibleDownloadsNotFromUserForThisAssignment (current_user.id, assignment_id)
		
	else:
		# Get an array of filenames not belonging to current user
		previous_download_file_id = completed_comments_ids_and_file_id[0][0]
		files_not_from_user = Upload.getPossibleDownloadsNotFromUserForThisAssignment (current_user.id, assignment_id, previous_download_file_id)
	
	number_of_files = len(files_not_from_user)
	if number_of_files == 0:
		flash('There are no files currently available for download. Please check back soon.')
		return redirect(url_for('assignments.view_assignments'))
	random_number = (randint(0,(number_of_files-1)))
	filename = files_not_from_user[random_number]
	random_file = os.path.join (current_app.config['UPLOAD_FOLDER'], filename)
	
	# Send SQL data to database
	download = Download(filename=filename, user_id = current_user.id)
	db.session.add(download)
	db.session.commit()
	
	# Update comments table with pending commment
	conditions = []
	conditions.append (str('filename="' + str(filename) + '"'))
	upload_id = app.models.selectFromDb(['id'], 'upload', conditions)
	comment_pending = Comment(user_id = int(current_user.id), file_id = int(upload_id[0][0]), pending = True, assignment_id=assignment_id)
	db.session.add(comment_pending)
	db.session.commit()

	return send_file(random_file, as_attachment=True)



# Download a file for peer review
@bp.route("/download_file")
@bp.route("/download_file/<assignment_id>")
@login_required
def download_file(assignment_id = False):
	if app.assignments.models.check_if_assignment_is_over (assignment_id) == True:
		return render_template('files/download_file.html', assignment_id = assignment_id)
	else:
		# If the assignment hasn't closed yet, flash message to wait until after deadline
		flash ("The assignment hasn't closed yet. Please wait until the deadline is over, then try again to download an assignment to review.")
		return redirect (url_for('assignments.view_assignments'))


# Student form to upload a file to an assignment
@bp.route('/upload/<assignment_id>',methods=['GET', 'POST'])
@login_required
def upload_file(assignment_id):
	# If the form has been filled out and posted:
	if request.method == 'POST':
		if 'file' not in request.files:
			flash('No file uploaded. Please try again or contact your tutor.')
			return redirect(request.url)
		file = request.files['file']
		if file.filename == '':
			flash('The filename is blank. Please rename the file.')
			return redirect(request.url)
		if file and models.allowed_file_extension(file.filename):
			models.save_assignment_file(file, assignment_id)
			original_filename = models.get_secure_filename(file.filename)
			flash('Your file ' + str(original_filename) + ' successfully uploaded')
			return redirect(url_for('assignments.view_assignments'))
		else:
			flash('You can not upload this kind of file.')
			return redirect(url_for('assignments.view_assignments'))
	else:
		return render_template('files/upload_file.html')

	

@bp.route("/comments/<file_id>")
@login_required
def view_comments(file_id):
	#!# What about admin?
	if current_user.id is models.get_file_owner_id (file_id):
		original_filename = models.get_upload_filename_from_upload_id (file_id)
		comments = models.get_peer_reviews_from_upload_id (file_id)	
		return render_template('files/view_comments.html', comments = comments, original_filename = original_filename)
	abort (403)
		
	
# Display an empty review feedback form
@bp.route("/peer_review_form/<assignment_id>", methods=['GET', 'POST'])
@bp.route("/peer_review_form", methods=['GET', 'POST'])
@login_required
def create_peer_review(assignment_id = False):
	# Get the appropriate peer review form for the assignment via assignment ID
	if assignment_id:
		peer_review_form = Assignment.getPeerReviewFormFromAssignmentId(assignment_id)
		peer_review_form_name = peer_review_form[0][0]	
		form = eval(peer_review_form_name)()
	
	if form.validate_on_submit():
		# Serialise the form contents
		form_fields = {}
		for field_title, field_contents in form.data.items():
			form_fields[field_title] = field_contents
		# Clean the csrf_token and submit fields
		del form_fields['csrf_token']
		del form_fields['submit']
		form_contents = json.dumps(form_fields)
		
		# Check if user has any previous downloads with pending peer reviews
		pending_assignments = Comment.getPendingStatusFromUserIdAndAssignmentId (current_user.id, assignment_id)
		if len(pending_assignments) > 0:
			# User has a pending peer review - update the empty comment field with the contents of this form and remove pending status
			pending_comment_id = pending_assignments[0][0]
			update_comment = Comment.updatePendingCommentWithComment(pending_comment_id, form_contents)
		
		# The database is now updated with the comment - check the total completed comments
		completed_comments = Comment.getCountCompleteCommentsFromUserIdAndAssignmentId (current_user.id, assignment_id)
		if completed_comments[0][0] == 1:
			# This is the first peer review, submit
			flash('Peer review 1 submitted succesfully!')
		elif completed_comments[0][0] == 2:
			# This is the second peer review, submit
			flash('Peer review 2 submitted succesfully!')
		return redirect(url_for('assignments.view_assignments'))
	return render_template('files/peer_review_form.html', title='Submit a peer review', form=form)


# Display an empty review feedback form
@bp.route("/create_teacher_review/<upload_id>", methods=['GET', 'POST'])
@login_required
def create_teacher_review(upload_id):
	# Get the appropriate peer review form
	peer_review_form = models.get_peer_review_form_from_upload_id (upload_id)
	form = eval(peer_review_form)()
	
	if form.validate_on_submit():
		# Serialise the form contents
		form_fields = {}
		for field_title, field_contents in form.data.items():
			form_fields[field_title] = field_contents
		# Clean the csrf_token and submit fields
		del form_fields['csrf_token']
		del form_fields['submit']
		form_contents = json.dumps(form_fields)
		
		update_comment = models.add_teacher_comment_to_upload(form_contents, upload_id)
		
		flash('Teacher review submitted succesfully!')
		return redirect(url_for('assignments.view_assignments'))
	return render_template('files/peer_review_form.html', title='Submit a teacher review', form=form)


# View a completed and populated peer review form
# This accepts both the user's own peer reviews, and other users' reviews
@bp.route("/view_peer_review_from_assignment/<assignment_id>/<peer_review_number>", methods=['GET', 'POST'])
@bp.route("/view_peer_comment/<comment_id>", methods=['GET', 'POST'])
@login_required
def view_peer_review(assignment_id = False, peer_review_number = False, comment_id = False):
	if comment_id:
		# Check if this peer review is intended for the user trying to view it
		# What file was it made for
		file_id = app.models.selectFromDb(['file_id'], 'comment', [str('id="' + str(comment_id) + '"')])
		# Who owns that file
		owner = app.models.selectFromDb(['user_id'], 'upload', [str('id="' + str(file_id[0][0]) + '"')])
		# Is it the same person trying to view this comment?
		if current_user.id is not owner[0][0]:
			abort (403)
		
		# Get assignment ID from comment ID
		assignment_id = app.models.selectFromDb(['assignment_id'],'comment',[(str('id="'+str(comment_id)+'"'))])
		# Get the form from the assignmentId
		peer_review_form_name = app.models.selectFromDb(['peer_review_form'],'assignment',[(str('id="'+str(assignment_id[0][0])+'"'))])
		
		# Get the comment content from ID
		comment = app.models.selectFromDb(['comment'],'comment',[(str('id="'+str(comment_id)+'"'))])
		unpacked_comments = json.loads(comment[0][0])
	else:
		# Get the form from the assignmentId	
		peer_review_form_name = app.models.selectFromDb(['peer_review_form'],'assignment',[(str('id="'+str(assignment_id)+'"'))])
		# Get the first or second peer review - these will be in created order in the DB
		conditions = []
		conditions.append (str('assignment_id="' + str(assignment_id) + '"'))
		conditions.append (str('user_id="' + str(current_user.id) + '"'))
		comments = app.models.selectFromDb(['comment'],'comment',conditions)
		if int(peer_review_number) == 1:
			unpacked_comments = json.loads(comments[0][0])
		elif int(peer_review_number) == 2:
			unpacked_comments = json.loads(comments[1][0])
		flash('You can not edit this peer review as it has already been submitted.')
	
	# Import the form class
	form_class = getattr(app.forms_peer_review, str(peer_review_form_name[0][0]))
	# Populate the form
	form = form_class(**unpacked_comments)
	# Delete submit button
	del form.submit
	
	return render_template('files/peer_review_form.html', title='View a peer review', form=form)