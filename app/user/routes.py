from flask import render_template, redirect, url_for, session, flash, request, abort, current_app
import datetime

# Login
from flask_login import current_user, login_user, login_required, logout_user
from werkzeug.urls import url_parse

# Register
from app.models import User, Turma
from app import db

# Utility classes
import app.email_model

# Forms
import app.main.forms
from app.user import bp, models, forms

from app import executor

# Log-in page
@bp.route('/login', methods=['GET', 'POST'])
def login():
	if current_user.is_authenticated:
		return redirect(url_for('main.index'))
	form = app.user.forms.LoginForm()
	if form.validate_on_submit():
		user = User.query.filter_by(username=form.username.data).first()
		if user is None or not user.check_password(form.password.data):
			flash('Invalid username or password')
			return redirect(url_for('user.login'))
		# Check for email validation
		if User.user_email_is_confirmed(user.username) == False:
			flash('Please confirm your email.')
			return redirect(url_for('user.login'))
		
		login_user(user, remember=form.remember_me.data)
		next_page = request.args.get('next')
		if not next_page or url_parse(next_page).netloc != '':
			next_page = url_for('main.index')
		return redirect(next_page)
	return render_template('user/login.html', title='Sign In', form=form)



# Log-out page
@bp.route('/logout')
def logout():
	logout_user()
	return redirect(url_for('main.index'))

############## User registration, log-in/out, and management

# Registration
@bp.route('/register', methods=['GET', 'POST'])
def register():
	if current_user.is_authenticated and app.models.is_admin(current_user.username) is not True:
		return redirect(url_for('main.index'))
	if current_app.config['REGISTRATION_IS_OPEN'] == True:
		form = app.user.forms.RegistrationForm()
		form.target_turmas.choices = [(turma.id, turma.turma_label) for turma in Turma.query.all()]
		if form.validate_on_submit():
			if form.signUpCode.data in current_app.config['SIGNUP_CODES']:
				user = User(username=form.username.data, email=form.email.data, student_number=form.student_number.data)
				user.set_password(form.password.data)
				db.session.add(user)
				db.session.flush() # Access the new user.id field in the next step
				for turma_id in form.target_turmas.data:
					app.assignments.models.enroll_user_in_class(user.id, turma_id)
				db.session.commit()
				
				# Send the email confirmation link
				subject = "workUp - confirm your email"
				token = app.email_model.ts.dumps(str(form.email.data), salt=current_app.config["TS_SALT"])
				confirm_url = url_for('user.confirm_email', token=token, _external=True)
				html = render_template('email/activate.html',confirm_url=confirm_url)
				executor.submit(app.email_model.send_email, user.email, subject, html)
				
				flash('Congratulations, you are now a registered user! Please confirm your email.')
				return redirect(url_for('user.login'))
			else:
				flash("Please ask your tutor for sign-up instructions.")
				return redirect(url_for('user.login'))
		return render_template('user/register.html', title='Register', form=form)
	else:
		flash("Sign up is currently closed.")
		return redirect(url_for('main.index'))

# Confirm email
@bp.route('/confirm/<token>')
def confirm_email(token):
	try:
		email = app.email_model.ts.loads(token, salt=current_app.config["TS_SALT"], max_age=86400)
	except:
		abort(404)
	user = User.query.filter_by(email=email).first_or_404()
	user.email_confirmed = True
	db.session.add(user)
	db.session.commit()
	flash('Your email has been confirmed. Please log-in now.')
	return redirect(url_for('user.login'))

# Reset password form
@bp.route('/reset', methods=["GET", "POST"])
def reset():
	form = app.user.forms.EmailForm()
	if form.validate_on_submit():
		user = User.query.filter_by(email=form.email.data).first_or_404()
		subject = "Password reset requested"
		token = app.email_model.ts.dumps(user.email, salt=current_app.config["TS_RECOVER_SALT"])

		recover_url = url_for('user.reset_with_token', token=token, _external=True)
		html = render_template('email/recover.html', recover_url=recover_url)
		
		executor.submit(app.email_model.send_email, user.email, subject, html)
		flash('An email has been sent to your inbox with a link to recover your password.')
		return redirect(url_for('main.index'))
		
	return render_template('user/reset.html', form=form)

# Reset password with token
@bp.route('/reset/<token>', methods=["GET", "POST"])
def reset_with_token(token):
	try:
		email = app.email_model.ts.loads(token, salt=current_app.config['TS_RECOVER_SALT'], max_age=current_app.config['TS_MAX_AGE'])
	except:
		abort(404)
	form = app.user.forms.PasswordForm()
	if form.validate_on_submit():
		user = User.query.filter_by(email=email).first_or_404()
		user.set_password(form.password.data)
		db.session.commit()
		flash('Your password has been changed. You can now log-in with your new password.')
		return redirect(url_for('user.login'))
	return render_template('user/reset_with_token.html', form=form, token=token)


@bp.route('/edit/<user_id>', methods=['GET', 'POST'])
def edit_user(user_id):
	if current_user.is_authenticated and app.models.is_admin(current_user.username):
		user = User.query.get(user_id)
		form = app.user.forms.EditUserForm(obj=user)
		form.target_turmas.choices = [(turma.id, turma.turma_label) for turma in Turma.query.all()]
		if form.validate_on_submit():
			user.username = form.username.data
			user.email = form.email.data
			user.student_number = form.student_number.data
			app.assignments.models.reset_user_enrollment(user.id)
			for turma_id in form.target_turmas.data:
				app.assignments.models.enroll_user_in_class(user.id, turma_id)
			
			db.session.commit()
			flash('User edited successfully.')
			return redirect(url_for('user.manage_students'))
		return render_template('user/register.html', title='Edit user', form=form)

# Manage Users
@bp.route('/students/manage')
@login_required
def manage_students():
	if current_user.is_authenticated and app.models.is_admin(current_user.username):
		student_info = app.user.models.get_all_student_info()
		return render_template('user/manage_students.html', title='Manage students', student_info = student_info)
	abort(403)
	
# Manage Users
@bp.route('/teachers/manage')
@login_required
def manage_teachers():
	if current_user.is_authenticated and app.models.is_admin(current_user.username):
		teacher_info = app.user.models.get_all_admin_info()
		return render_template('user/manage_teachers.html', title='Manage teachers', teacher_info = teacher_info)
	abort(403)
	

# Convert normal user into admin
@bp.route('/give_admin_rights/<user_id>')
@login_required
def give_admin_rights(user_id):
	if current_user.is_authenticated and app.models.is_admin(current_user.username):
		try:
			# Make DB call to convert user into admin
			app.models.User.give_admin_rights(user_id)
			flash('User successfully made into administrator.')
		except:
			flash('An error occured when changing the user to an administrator.')
		return redirect(url_for('user.manage_students'))
	else:
		abort(403)
		
# Remove admin rights from user
@bp.route('/remove_admin_rights/<user_id>')
@login_required
def remove_admin_rights(user_id):
	if current_user.is_authenticated and app.models.is_admin(current_user.username):
		try:	
			app.models.User.remove_admin_rights(user_id)
			flash('Administrator rights removed from the user.')
		except:
			flash('An error occured when changing the user to an administrator.')
		return redirect(url_for('user.manage_students'))
	else:
		abort(403)


# Admin Registration
@bp.route('/register_admin', methods=['GET', 'POST'])
@login_required
def register_admin():
	if current_user.is_authenticated and app.models.is_admin(current_user.username):
		form = forms.AdminRegistrationForm()
		if form.validate_on_submit():
			user = User(username=form.username.data, email=form.email.data, is_admin = True)
			user.set_password(form.password.data)
			db.session.add(user)
			db.session.commit()
			
			# Send the email confirmation link
			subject = "Confirm new admin user"
			token = app.email_model.ts.dumps(str(form.email.data), salt=current_app.config["TS_SALT"])
			confirm_url = url_for('user.confirm_email', token=token, _external=True)
			html = render_template('email/activate.html',confirm_url=confirm_url)
			executor.submit(app.email_model.send_email, user.email, subject, html)
			
			flash('Congratulations, you are now a registered admin! Please confirm your email.')
			return redirect(url_for('user.login'))
		return render_template('user/register_admin.html', title='Register Admin', form=form)
	else:
		abort(403)


# Admin page to batch import and create users from an xls file
@bp.route("/batch_import_students", methods=['GET', 'POST'])
@login_required
def batch_import_students():
	if current_user.is_authenticated and app.models.is_admin(current_user.username):
		form = forms.BatchStudentImportForm()
		form.target_turmas.choices = [(turma.id, turma.turma_label) for turma in Turma.query.all()]
		if form.validate_on_submit():
			if not form.excel_file.data.filename:
				flash('No file uploaded. Please try again or contact your tutor.')
				return redirect(request.url)
			file = form.excel_file.data
			if file and models.check_if_excel_spreadsheet(file.filename):
				#models.save_excel_student_sheet(file)
				#original_filename = models.get_secure_filename(file.filename)
				session['student_info_array'] = models.process_student_excel_spreadsheet (file)
				return redirect(url_for('user.batch_import_students_preview', turma_id = form.target_course.data))
			else:
				flash('You can not upload this kind of file. You must upload an Excel (.xls) file.')
				return redirect(url_for('user.batch_import_students'))
		return render_template('user/batch_import_students.html', title='Batch import students', form=form)
	abort(403)

# Admin page to preview batch import
@bp.route("/batch_import_students_preview/<turma_id>")
@login_required
def batch_import_students_preview(turma_id):
	if current_user.is_authenticated and app.models.is_admin(current_user.username):
		return render_template('user/batch_import_students_preview.html', turma_id = turma_id, student_info_array = session.get('student_info_array', {}), title='Batch import students preview')
	abort(403)

# Admin page to display after the import process
@bp.route("/batch_import_students_process/<turma_id>")
@login_required
def batch_import_students_process(turma_id):
	if current_user.is_authenticated and app.models.is_admin(current_user.username):
		student_info_array = session.get('student_info_array', {})
		models.add_users_from_excel_spreadsheet(student_info_array, turma_id)
		return render_template('user/batch_import_students_process.html', student_info_array = session.get('student_info_array', {}), title='Batch import students process')
	abort(403)