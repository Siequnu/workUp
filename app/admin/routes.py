from flask import render_template, flash, redirect, url_for, request, current_app, abort
from flask_login import current_user

from app.admin.forms import TurmaCreationForm, AdminRegistrationForm
from app import db

from app.models import Assignment, Upload, Comment, Turma, User
import app.models
import app.assignments


# Login
from flask_login import login_required

# Blueprint
from app.admin import bp
	
	
# Admin page to set new class
@bp.route("/create_class", methods=['GET', 'POST'])
@login_required
def create_class():
	if current_user.is_authenticated and app.models.is_admin(current_user.username):
		form = app.admin.forms.TurmaCreationForm()
		if form.validate_on_submit():
			newTurma = Turma(turma_number=form.turmaNumber.data, turma_label=form.turmaLabel.data, turma_term=form.turmaTerm.data,
							 turma_year = form.turmaYear.data)
			db.session.add(newTurma)
			db.session.commit()
			flash('Class successfully created! You need to restart the flask app in order for this class to appear on the Assignment creation forms.')
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
		
		
# Convert normal user into admin
@bp.route('/give_admin_rights/<user_id>', methods=['GET', 'POST'])
@login_required
def give_admin_rights(user_id):
	if current_user.is_authenticated and app.models.is_admin(current_user.username):
		try:
			# Make DB call to convert user into admin
			app.models.User.give_admin_rights(user_id)
			flash('User successfully made into administrator.')
		except:
			flash('An error occured when changing the user to an administrator.')
		return redirect(url_for('admin.manage_users'))
	else:
		abort(403)
		
# Remove admin rights from user
@bp.route('/remove_admin_rights/<user_id>', methods=['GET', 'POST'])
@login_required
def remove_admin_rights(user_id):
	if current_user.is_authenticated and app.models.is_admin(current_user.username):
		try:	
			app.models.User.remove_admin_rights(user_id)
			flash('Administrator rights removed from the user.')
		except:
			flash('An error occured when changing the user to an administrator.')
		return redirect(url_for('admin.manage_users'))
	else:
		abort(403)


# Admin Registration
@bp.route('/manage_users', methods=['GET', 'POST'])
@login_required
def manage_users():
	if current_user.is_authenticated and app.models.is_admin(current_user.username):
		user_data = app.models.User.get_all_user_info()
		return render_template('admin/manage_users.html', title='Manage Users', user_data = user_data)
	abort(403)
