from app import workUpApp

from flask import render_template, redirect, url_for, session, flash, request, abort
import datetime

# Login
from flask_login import current_user, login_user
from flask_login import login_required
from werkzeug.urls import url_parse

# Logout
from flask_login import logout_user

# Register
from app.models import User
from app import db

# Utility classes
import app.email

# Forms
import app.forms
from app.user import bp

# Log-in page
@bp.route('/login', methods=['GET', 'POST'])
def login():
	if current_user.is_authenticated:
		return redirect(url_for('index'))
	form = app.user.forms.LoginForm()
	if form.validate_on_submit():
		user = User.query.filter_by(username=form.username.data).first()
		if user is None or not user.check_password(form.password.data):
			flash('Invalid username or password')
			return redirect(url_for('user.login'))
		# Check for email validation
		if User.checkEmailConfirmationStatus(user.username) == False:
			flash('Please confirm your email.')
			return redirect(url_for('user.login'))
		
		login_user(user, remember=form.remember_me.data)
		next_page = request.args.get('next')
		if not next_page or url_parse(next_page).netloc != '':
			next_page = url_for('index')
		return redirect(next_page)
	return render_template('user/login.html', title='Sign In', form=form)



# Log-out page
@bp.route('/logout')
def logout():
	logout_user()
	return redirect(url_for('index'))



# Registration
@bp.route('/register', methods=['GET', 'POST'])
def register():
	if current_user.is_authenticated:
		return redirect(url_for('index'))
	if workUpApp.config['REGISTRATION_IS_OPEN'] == True:
		form = app.user.forms.RegistrationForm()
		if form.validate_on_submit():
			if form.signUpCode.data in workUpApp.config['SIGNUP_CODES']:
				user = User(username=form.username.data, email=form.email.data, studentnumber=form.studentNumber.data, turma_id=form.turmaId.data)
				user.set_password(form.password.data)
				db.session.add(user)
				db.session.commit()
				
				# Send the email confirmation link
				subject = "Confirm your email"
				token = app.email.ts.dumps(str(form.email.data), salt=workUpApp.config["TS_SALT"])
				confirm_url = url_for('user.confirm_email', token=token, _external=True)
				html = render_template('email/activate.html',confirm_url=confirm_url)
				app.email.sendEmail (user.email, subject, html)
				
				flash('Congratulations, you are now a registered user! Please confirm your email.')
				return redirect(url_for('user.login'))
			else:
				flash("Please ask your tutor for sign-up instructions.")
				return redirect(url_for('user.login'))
		return render_template('user/register.html', title='Register', form=form)
	else:
		flash("Sign up is currently closed.")
		return redirect(url_for('index'))



# Confirm email
@bp.route('/confirm/<token>')
def confirm_email(token):
	try:
		email = app.email.ts.loads(token, salt=workUpApp.config["TS_SALT"], max_age=86400)
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
		token = app.email.ts.dumps(user.email, salt=workUpApp.config["TS_RECOVER_SALT"])

		recover_url = url_for('user.reset_with_token', token=token, _external=True)
		html = render_template('email/recover.html', recover_url=recover_url)
		
		app.email.sendEmail(user.email, subject, html)
		flash('An email has been sent to your inbox with a link to recover your password.')
		return redirect(url_for('index'))
		
	return render_template('user/reset.html', form=form)



# Reset password with token
@bp.route('/reset/<token>', methods=["GET", "POST"])
def reset_with_token(token):
	try:
		email = app.email.ts.loads(token, salt=workUpApp.config['TS_RECOVER_SALT'], max_age=workUpApp.config['TS_MAX_AGE'])
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


	


