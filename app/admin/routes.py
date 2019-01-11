from flask import render_template, flash, redirect, url_for, request, current_app, abort
from flask_login import current_user

from app.admin.forms import AssignmentCreationForm, TurmaCreationForm, AdminRegistrationForm
from app import db

from app.models import Assignment, Upload, Comment, Turma, User
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
	if current_user.is_authenticated and app.models.is_admin(current_user.username):
		form = app.admin.forms.AssignmentCreationForm()
		if form.validate_on_submit():
			assignment = Assignment(title=form.title.data, description=form.description.data, due_date=form.due_date.data,
								target_course=form.target_course.data, created_by_id=current_user.id, peer_review_form=form.peer_review_form.data)
			db.session.add(assignment)
			db.session.commit()
			flash('Assignment successfully created!')
			return redirect(url_for('assignments.view_assignments'))
		return render_template('admin/create_assignment.html', title='Create Assignment', form=form)
	abort(403)
	
	
# Delete all user uploads and comments associated with this assignment
@bp.route("/deleteassignment/<assignmentId>")
@login_required
def deleteAssignment(assignmentId):
	if current_user.is_authenticated and app.models.is_admin(current_user.username):
		# Delete the assignment
		app.assignments.models.deleteAssignmentFromId(assignmentId)
		# Delete all uploads for this assignment
		Upload.deleteAllUploadsFromAssignmentId(assignmentId)
		# Download records are not deleted for future reference
		# Delete all comments for those uploads
		Comment.deleteCommentsFromAssignmentId(assignmentId)
		
		flash('Assignment ' + str(assignmentId) + ', and all related uploaded files and comments have been deleted from the db. Download records have been kept.')
		return redirect(url_for('assignments.view_assignments'))
	abort (403)
	
	
	
# Admin page to set new class
@bp.route("/createclass", methods=['GET', 'POST'])
@login_required
def createClass():
	if current_user.is_authenticated and app.models.is_admin(current_user.username):
		form = app.admin.forms.TurmaCreationForm()
		if form.validate_on_submit():
			newTurma = Turma(turma_number=form.turmaNumber.data, turma_label=form.turmaLabel.data, turma_term=form.turmaTerm.data,
							 turma_year = form.turmaYear.data)
			db.session.add(newTurma)
			db.session.commit()
			flash('Class successfully created!')
			return redirect(url_for('admin.classAdmin'))
		return render_template('admin/create_class.html', title='Create new class', form=form)
	abort(403)
	



# Admin page to view classes
@bp.route("/classadmin")
@login_required
def classAdmin():
	if current_user.is_authenticated and app.models.is_admin(current_user.username):
		classesArray = app.models.selectFromDb(['*'], 'turma')
		return render_template('admin/class_admin.html', title='Class admin', classesArray = classesArray)
	abort (403)
	
	
			
# Delete a class
@bp.route("/deleteclass/<turmaId>")
@login_required
def deleteClass(turmaId):
	if current_user.is_authenticated and app.models.is_admin(current_user.username):
		Turma.deleteTurmaFromId(turmaId)
		flash('Class ' + str(turmaId) + ' has been deleted.')
		return redirect(url_for('admin.classAdmin'))		
	abort (403)



# Admin Registration
@bp.route('/register_admin', methods=['GET', 'POST'])
@login_required
def register_admin():
	if current_user.is_authenticated and app.models.is_admin(current_user.username):
		form = app.admin.forms.AdminRegistrationForm()
		if form.validate_on_submit():
			user = User(username=form.username.data, email=form.email.data, is_admin = True)
			user.set_password(form.password.data)
			db.session.add(user)
			db.session.commit()
			
			# Send the email confirmation link
			subject = "Confirm new admin user"
			token = app.email.ts.dumps(str(form.email.data), salt=current_app.config["TS_SALT"])
			confirm_url = url_for('user.confirm_email', token=token, _external=True)
			html = render_template('email/activate.html',confirm_url=confirm_url)
			app.email.sendEmail (user.email, subject, html)
			
			flash('Congratulations, you are now a registered admin! Please confirm your email.')
			return redirect(url_for('user.login'))
		return render_template('admin/register_admin.html', title='Register Admin', form=form)
	else:
		abort(403)


# Admin Registration
@bp.route('/manage_users', methods=['GET', 'POST'])
@login_required
def manage_users():
	if current_user.is_authenticated and app.models.is_admin(current_user.username):
		admin_usernames = app.models.User.get_admin_users_list()
		return render_template('admin/manage_users.html', title='Manage Users', )
	abort(403)
