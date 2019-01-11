from flask import render_template, flash, redirect, url_for, request, current_app, abort
from flask_login import current_user, login_required

from app.assignments import bp, models
import app.models

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