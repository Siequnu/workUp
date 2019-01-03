from app import workUpApp

from flask import render_template, flash, redirect, url_for, request
from flask_login import current_user

from app.admin.forms import AssignmentCreationForm, TurmaCreationForm
from app import db

from app.models import Assignment, Upload, Comment, Turma
import app.models
import app.assignments


# Login
from flask_login import login_required

# Blueprint
from app.admin import bp

# Admin page to set new assignment
@bp.route("/createassignment", methods=['GET', 'POST'])
@login_required
def createAssignment():
	if current_user.is_authenticated:
		if current_user.username in workUpApp.config['ADMIN_USERS']:
			form = app.admin.forms.AssignmentCreationForm()
			if form.validate_on_submit():
				assignment = Assignment(title=form.title.data, description=form.description.data, due_date=form.due_date.data,
									target_course=form.target_course.data, created_by_id=current_user.id, peer_review_form=form.peer_review_form.data)
				db.session.add(assignment)
				db.session.commit()
				flash('Assignment successfully created!')
				return redirect(url_for('main.viewAssignments'))
			return render_template('admin/create_assignment.html', title='Create Assignment', form=form)

	
	
# Delete all user uploads and comments associated with this assignment
@bp.route("/deleteassignment/<assignmentId>")
@login_required
def deleteAssignment(assignmentId):
	if current_user.username in workUpApp.config['ADMIN_USERS']:
		# Delete the assignment
		app.assignments.models.deleteAssignmentFromId(assignmentId)
		# Delete all uploads for this assignment
		Upload.deleteAllUploadsFromAssignmentId(assignmentId)
		# Download records are not deleted for future reference
		# Delete all comments for those uploads
		Comment.deleteCommentsFromAssignmentId(assignmentId)
		
		flash('Assignment ' + str(assignmentId) + ', and all related uploaded files and comments have been deleted from the db. Download records have been kept.')
		return redirect(url_for('main.viewAssignments'))
	abort (403)
	
	
	
# Admin page to set new class
@bp.route("/createclass", methods=['GET', 'POST'])
@login_required
def createClass():
	if current_user.is_authenticated:
		if current_user.username in workUpApp.config['ADMIN_USERS']:
			form = app.admin.forms.TurmaCreationForm()
			if form.validate_on_submit():
				newTurma = Turma(turma_number=form.turmaNumber.data, turma_label=form.turmaLabel.data, turma_term=form.turmaTerm.data,
								 turma_year = form.turmaYear.data)
				db.session.add(newTurma)
				db.session.commit()
				flash('Class successfully created!')
				return redirect(url_for('admin.classAdmin'))
			return render_template('admin/create_class.html', title='Create new class', form=form)



# Admin page to view classes
@bp.route("/classadmin")
@login_required
def classAdmin():
	if current_user.is_authenticated:
		if current_user.username in workUpApp.config['ADMIN_USERS']:
			classesArray = app.models.selectFromDb(['*'], 'turma')
			return render_template('admin/class_admin.html', title='Class admin', classesArray = classesArray)
	abort (403)
	
	
			
# Delete a class
@bp.route("/deleteclass/<turmaId>")
@login_required
def deleteClass(turmaId):
	if current_user.username in workUpApp.config['ADMIN_USERS']:
		Turma.deleteTurmaFromId(turmaId)
		flash('Class ' + str(turmaId) + ' has been deleted.')
		return redirect(url_for('admin.classAdmin'))		
	abort (403)
