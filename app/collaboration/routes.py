from flask import render_template, flash, redirect, url_for, request, abort, current_app, session, Response
from flask_login import current_user, login_required

from app.collaboration import bp

from app import db
from datetime import datetime
from app.models import Firepad, Collab, User, Enrollment


# Collaboration home page
@bp.route("/")
@login_required
def collaboration_index():
	#!# Filter by username, only get firepads by this owner
	firepads = Firepad.query.filter_by(owner_id=current_user.id).all()
	
	# Collabs
	#!# Filter by username to only get invites
	collabs = Collab.query.filter_by(user_id=current_user.id).all()
	print (firepads, collabs)
	return render_template('collaboration/collaboration_index.html', firepads = firepads, collabs = collabs)


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
	#!# Check if is owner or collab, otherwise 403
	collaborators = db.session.query(
		Collab, User).join(
		User, Collab.user_id == User.id).filter(
		Collab.firepad_id==firepad_id)
	return render_template('collaboration/firepad.html',
							api_key = current_app.config['FIREBASE_API_KEY'],
							auth_domain = current_app.config['FIREBASE_AUTH_DOMAIN'],
							database_url = current_app.config['FIREBASE_DATABASE_URL'],
							collaborators = collaborators,
							firepad_id = firepad_id)


# Form to find new user
@bp.route("/find/<firepad_id>")
@login_required
def find_user(firepad_id):
	# If admin, display all students, with shortcut to add entire classes
	
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
	#!# Check if this is the owner or an admin
	user = User.query.get(user_id)
	collab = Collab (user_id = user_id, firepad_id = firepad_id)
	db.session.add(collab)
	db.session.commit()
	flash ('Successfully added ' + user.username + ' to the pad', 'success')
	return redirect(url_for('collaboration.collaborate', firepad_id = firepad_id))


# Method to remove a user from a pad
@bp.route("/remove/<user_id>/<firepad_id>")
@login_required
def remove_user(user_id, firepad_id):
	#!# Check if this is the owner or an admin
	user = User.query.get(user_id)
	collab = Collab.query.filter_by(user_id = user_id).filter_by(firepad_id = firepad_id).one()
	
	db.session.delete(collab)
	db.session.commit()
	flash ('Successfully removed ' + user.username + ' from the pad', 'success')
	return redirect(url_for('collaboration.collaborate', firepad_id = firepad_id))