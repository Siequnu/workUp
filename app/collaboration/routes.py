from flask import render_template, flash, redirect, url_for, request, abort, current_app, session, Response
from flask_login import current_user, login_required

from app.collaboration import bp, models

from app import db
from datetime import datetime
from app.models import Firepad, Collab, User, Enrollment
import app.models


# Collaboration home page
@bp.route("/")
@login_required
def collaboration_index():
	firepads = Firepad.query.filter_by(owner_id=current_user.id).all()
	firepads_info_array = []
	for firepad in firepads:
		firepad_dict = firepad.__dict__
		firepad_dict['owner'] = app.collaboration.models.get_firepad_owner_user_object(firepad.id)
		firepad_dict['collaborators'] = app.collaboration.models.get_firepad_collaborator_user_objects(firepad.id)
		firepads_info_array.append(firepad_dict)
	
	# Collabs
	collabs = Collab.query.filter_by(user_id=current_user.id).all()
	collabs_info_array = []
	for collab in collabs:
		collab_dict = collab.__dict__
		collab_dict['owner'] = app.collaboration.models.get_firepad_owner_user_object(collab.firepad_id)
		collab_dict['collaborators'] = app.collaboration.models.get_firepad_collaborator_user_objects(collab.firepad_id)
		collabs_info_array.append(collab_dict)
	
	return render_template('collaboration/collaboration_index.html', firepads = firepads_info_array, collabs = collabs_info_array)


# Create new firepad as owner
@bp.route("/new")
@login_required
def create_new_firepad():
	firepad = Firepad(owner_id=current_user.id, timestamp = datetime.now())
	db.session.add(firepad)
	db.session.flush() # Access the new firepad ID in the redirect
	db.session.commit()
	return redirect(url_for('collaboration.collaborate', firepad_id = firepad.id))

@bp.route("/<firepad_id>")
@login_required
def collaborate(firepad_id):
	if app.collaboration.models.check_if_user_has_access_to_firepad(firepad_id, current_user.id):
		is_owner = app.models.is_admin(current_user.username) or Firepad.query.get(firepad_id).owner_id == current_user.id
		owner = app.collaboration.models.get_firepad_owner_user_object(firepad_id)
		collaborators = db.session.query(
			Collab, User).join(
			User, Collab.user_id == User.id).filter(
			Collab.firepad_id==firepad_id).all()
		return render_template('collaboration/firepad.html',
							api_key = current_app.config['FIREBASE_API_KEY'],
							auth_domain = current_app.config['FIREBASE_AUTH_DOMAIN'],
							database_url = current_app.config['FIREBASE_DATABASE_URL'],
							collaborators = collaborators,
							owner = owner,
							is_owner = is_owner,
							firepad_id = firepad_id)
	else:
		flash ('You do not have permission to access this pad. Please ask the owner to add you as a collaborator', 'info')
		return redirect (url_for('collaboration.collaboration_index'))


# Form to find new user
@bp.route("/find/<firepad_id>")
@login_required
def find_user(firepad_id):
	# If admin, display all students, with shortcut to add entire classes
	if app.models.is_admin(current_user.username):
		classmates = db.session.query(
				User, Enrollment).join(
				Enrollment, User.id == Enrollment.user_id).all()
	else:
		
		# If student, get list of students from current class
		# Get user list for the current class
		enrollments = db.session.query(Enrollment.turma_id).filter(Enrollment.user_id==current_user.id).all()
		classmates = []
		for turma_id in enrollments[0]:
			class_list = db.session.query(
				User, Enrollment).join(
				Enrollment, User.id == Enrollment.user_id).filter(
				Enrollment.turma_id==turma_id).all()
			for student in class_list: classmates.append(student)
			
		# Display searchable table with username and button to add user
	return render_template('collaboration/find_user.html', classmates = classmates, firepad_id = firepad_id)

# Method to add new user to a pad
@bp.route("/add/<user_id>/<firepad_id>")
@login_required
def add_user(user_id, firepad_id):
	if app.models.is_admin(current_user.username) or Firepad.query.get(firepad_id).owner_id == current_user.id:
		if int(user_id) == int(current_user.id):
			flash ('You already have access to this pad', 'info')
			return redirect(url_for('collaboration.collaborate', firepad_id = firepad_id))
		else:
			user = User.query.get(user_id)
			collab = Collab (user_id = user_id, firepad_id = firepad_id)
			db.session.add(collab)
			db.session.commit()
			flash ('Successfully added ' + user.username + ' to the pad', 'success')
	else:
		flash ('Collaborators can only be added by the document owner', 'info')
	return redirect(url_for('collaboration.collaborate', firepad_id = firepad_id))


# Method to remove a user from a pad
@bp.route("/remove/<user_id>/<firepad_id>")
@login_required
def remove_user(user_id, firepad_id):
	if app.models.is_admin(current_user.username) or Firepad.query.get(firepad_id).owner_id == current_user.id:
		user = User.query.get(user_id)
		collab = Collab.query.filter_by(user_id = user_id).filter_by(firepad_id = firepad_id).one()
		
		db.session.delete(collab)
		db.session.commit()
		flash ('Successfully removed ' + user.username + ' from the pad', 'success')
	else:
		flash ('Only the owner can remove users from the pad', 'info')
	return redirect(url_for('collaboration.collaborate', firepad_id = firepad_id))