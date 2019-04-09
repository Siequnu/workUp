from flask import render_template, flash, redirect, url_for, request, current_app, abort
from flask_login import current_user, login_required

from app.assignments import bp, models, forms
from app.models import Assignment, Upload, Comment, Turma, User
import app.models
from app import db

# View created assignments status
@bp.route("/view_assignments")
@login_required
def view_assignments():
	if current_user.is_authenticated and app.models.is_admin(current_user.username):
		# Get admin view with all assignments
		cleanAssignmentsArray = app.assignments.models.getAllAssignments()
		return render_template('assignments/view_assignments.html', assignmentsArray = cleanAssignmentsArray, admin = True)
	elif current_user.is_authenticated:
		# Get user class
		turmaId = app.assignments.models.getUserTurmaFromId(current_user.id)
		if (turmaId == False):
			flash('You are not part of any class and can not see any assignments. Ask your tutor for help to join a class.')
			return render_template('assignments/view_assignments.html') # User isn't part of any class - display no assignments
		else:
			# Get assignments for this user
			cleanAssignmentsArray = app.assignments.models.getUserAssignmentInformation (current_user.id)
			return render_template('assignments/view_assignments.html', assignmentsArray = cleanAssignmentsArray)
	abort (403)


# Admin page to set new assignment
@bp.route("/create_assignment", methods=['GET', 'POST'])
@login_required
def create_assignment():
	if current_user.is_authenticated and app.models.is_admin(current_user.username):
		form = app.assignments.forms.AssignmentCreationForm()
		if form.validate_on_submit():
			assignment = Assignment(title=form.title.data, description=form.description.data, due_date=form.due_date.data,
								target_course=form.target_course.data, created_by_id=current_user.id,
								peer_review_necessary= form.peer_review_necessary, peer_review_form=form.peer_review_form.data)
			db.session.add(assignment)
			db.session.commit()
			flash('Assignment successfully created!')
			return redirect(url_for('assignments.view_assignments'))
		return render_template('assignments/create_assignment.html', title='Create Assignment', form=form)
	abort(403)
	

# Delete all user uploads and comments associated with this assignment
@bp.route("/delete_assignment/<assignment_id>")
@login_required
def delete_assignment(assignment_id):
	if current_user.is_authenticated and app.models.is_admin(current_user.username):
		# Delete the assignment
		app.assignments.models.delete_assignment_from_id(assignment_id)
		# Delete all uploads for this assignment
		Upload.deleteAllUploadsFromAssignmentId(assignment_id)
		# Download records are not deleted for future reference
		# Delete all comments for those uploads
		Comment.deleteCommentsFromAssignmentId(assignment_id)
		
		flash('Assignment ' + str(assignment_id) + ', and all related uploaded files and comments have been deleted from the database. Download records have been kept.')
		return redirect(url_for('assignments.view_assignments'))
	abort (403)
	