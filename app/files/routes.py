from flask import render_template, flash, redirect, url_for, request, current_app, send_file, abort
from flask_login import current_user

# Login
from flask_login import login_required
from app import db

# Models
import app.assignments.models

from app.files import bp
from app.files import models, forms
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
		print (template_packages['uploads_object'])
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
		filename = Upload.query.get(already_downloaded_and_pending_review_file_id).filename
		#conditions = []
		#conditions.append(str('id="' + str(already_downloaded_and_pending_review_file_id) + '"'))
		#filename_to_download = app.models.selectFromDb(['filename'], 'upload', conditions)		
		#file_path = os.path.join (current_app.config['UPLOAD_FOLDER'], filename_to_download[0][0])
		# Send SQL data to database
		#download = Download(filename=filename_to_download[0][0], user_id = current_user.id)
		#db.session.add(download)
		#db.session.commit()
		return models.download_file(filename)
		#return send_file(file_path, as_attachment=True)
	
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
	upload_id = Upload.query.filter_by(filename=filename).first().id
	comment_pending = Comment(user_id = int(current_user.id), file_id = int(upload_id),
							  pending = True, assignment_id=assignment_id)
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
		flash ("The assignment hasn't finished yet. Please wait until the deadline is over, then try again to download an assignment to review.")
		return redirect (url_for('assignments.view_assignments'))


# Download any file from ID
@bp.route("/download/<file_id>")
@login_required
def download (file_id):
	if current_user.is_authenticated and app.models.is_admin(current_user.username):
		filename = Upload.query.get(file_id).filename
		return models.download_file(filename, rename=True)


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
			flash('Your file ' + str(original_filename) + ' was submitted successfully.')
			return redirect(url_for('assignments.view_assignments'))
		else:
			flash('You can not upload this kind of file. Please use a iWork, Office or PDF document.')
			return redirect(url_for('assignments.view_assignments'))
	else:
		return render_template('files/upload_file.html')

	

@bp.route("/comments/<file_id>")
@login_required
def view_comments(file_id):
	if current_user.id is models.get_file_owner_id (file_id) or app.models.is_admin(current_user.username):
		original_filename = models.get_upload_filename_from_upload_id (file_id)
		comments = models.get_peer_reviews_from_upload_id (file_id)	
		return render_template('files/view_comments.html', comments = comments, original_filename = original_filename)
	abort (403)
	
	

	
@bp.route("/class_library/")
@login_required
def class_library():
	if app.models.is_admin(current_user.username):
		classes = app.assignments.models.get_all_class_info()
		library = app.files.models.get_all_library_books ()
		return render_template('files/class_library.html', admin = True, classes = classes, library = library)
	else:
		library = app.files.models.get_user_library_books_from_id (current_user.id)
		enrollment = app.assignments.models.get_user_enrollment_from_id(current_user.id)
		return render_template('files/class_library.html', library = library, enrollment = enrollment)
	abort (403)
	

# Admin form to upload a library file
@bp.route('/class_library/upload/',methods=['GET', 'POST'])
@login_required
def upload_library_file():
	if app.models.is_admin(current_user.username):	
		form = forms.LibraryUploadForm()
		if form.validate_on_submit():
			app.files.models.new_library_upload_from_form(form)
			flash('New file successfully added to the library!')
			return redirect(url_for('files.class_library'))
		return render_template('files/upload_library_file.html', title='Upload library file', form=form)
	abort (403)
	

# Admin form to upload a library file
@bp.route('/class_library/delete/<library_upload_id>')
@bp.route('/class_library/delete/<library_upload_id>/<turma_id>')
@login_required
def delete_library_file(library_upload_id, turma_id = False):
	if app.models.is_admin(current_user.username):	
		app.files.models.delete_library_upload_from_id(library_upload_id, turma_id)
		flash('File deleted from the library!')
		return redirect(url_for('files.class_library'))
	abort (403)