from flask import render_template, flash, redirect, url_for, request, current_app, abort
from flask_login import current_user, login_required

from app.assignments import bp, models, forms
from app.assignments.forms import TurmaCreationForm, AssignmentCreationForm
from app.files import models
from app.models import Assignment, Upload, Comment, Turma, User, AssignmentTaskFile
import app.models

from app import db

########## Student class (turma) methods
@bp.route("/create_class", methods=['GET', 'POST'])
@login_required
def create_class():
	if current_user.is_authenticated and app.models.is_admin(current_user.username):
		form = forms.TurmaCreationForm()
		if form.validate_on_submit():
			newTurma = Turma(turma_number=form.turmaNumber.data, turma_label=form.turmaLabel.data, turma_term=form.turmaTerm.data,
							 turma_year = form.turmaYear.data)
			db.session.add(newTurma)
			db.session.commit()
			flash('Class successfully created! You need to restart the flask app in order for this class to appear on the Assignment creation forms.')
			return redirect(url_for('assignments.class_admin'))
		return render_template('assignments/create_class.html', title='Create new class', form=form)
	abort(403)

@bp.route("/classadmin")
@login_required
def class_admin():
	if current_user.is_authenticated and app.models.is_admin(current_user.username):
		classesArray = app.models.selectFromDb(['*'], 'turma')
		return render_template('assignments/class_admin.html', title='Class admin', classesArray = classesArray)
	abort (403)
			
@bp.route("/deleteclass/<turmaId>")
@login_required
def delete_class(turmaId):
	if current_user.is_authenticated and app.models.is_admin(current_user.username):
		Turma.deleteTurmaFromId(turmaId)
		flash('Class ' + str(turmaId) + ' has been deleted.')
		return redirect(url_for('assignments.class_admin'))		
	abort (403)
########################################

# View created assignments status
@bp.route("/view_assignments")
@login_required
def view_assignments():
	if current_user.is_authenticated and app.models.is_admin(current_user.username):
		# Get admin view with all assignments
		clean_assignments_array = app.assignments.models.get_all_assignments_info()
		return render_template('assignments/view_assignments.html', assignmentsArray = clean_assignments_array, admin = True)
	elif current_user.is_authenticated:
		# Get user class
		if User.get_user_turma_from_user_id(current_user.id) is not None:
			# Get assignments for this user
			clean_assignments_array = app.assignments.models.get_user_assignment_info (current_user.id)
			return render_template('assignments/view_assignments.html', assignmentsArray = clean_assignments_array)
		else:
			flash('You are not part of any class and can not see any assignments. Ask your tutor for help to join a class.')
			return render_template('assignments/view_assignments.html') # User isn't part of any class - display no assignments
	abort (403)


# View created assignments status
@bp.route("/view_assignment_details/<assignment_id>")
@login_required
def view_assignment_details(assignment_id):
	if current_user.is_authenticated and app.models.is_admin(current_user.username):
		# Get all files that have been uploaded for this assignment
		uploads_info = app.files.models.get_all_uploads_from_assignment_id(assignment_id)
		return render_template('assignments/view_assignment_details.html', uploads_info = uploads_info)
	abort (403)


# Admin page to set new assignment
@bp.route("/create_assignment", methods=['GET', 'POST'])
@login_required
def create_assignment():
	if current_user.is_authenticated and app.models.is_admin(current_user.username):
		form = app.assignments.forms.AssignmentCreationForm()
		if form.validate_on_submit():
			# Save assignment task file, if present
			if form.assignment_task_file.data is not None:
				file = form.assignment_task_file.data
				random_filename = app.files.models.save_file(file)
				original_filename = app.files.models.get_secure_filename(file.filename)
				assignment_task_file = AssignmentTaskFile (original_filename=original_filename,
													   filename = random_filename,
													   user_id = current_user.id)
				db.session.add(assignment_task_file)
				db.session.flush() # Acess the assingment_task_file.id field from db
			
			if form.assignment_task_file.data is not None:
				assignment = Assignment(title=form.title.data, description=form.description.data, due_date=form.due_date.data,
								target_turma_id=form.target_turma_id.data, created_by_id=current_user.id,
								peer_review_necessary= form.peer_review_necessary.data,
								peer_review_form=form.peer_review_form.data,
								assignment_task_file_id=assignment_task_file.id)
			else:
				assignment = Assignment(title=form.title.data, description=form.description.data, due_date=form.due_date.data,
								target_turma_id=form.target_turma_id.data, created_by_id=current_user.id,
								peer_review_necessary= form.peer_review_necessary.data,
								peer_review_form=form.peer_review_form.data)
			
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
		if app.assignments.models.delete_assignment_from_id(assignment_id) == True:
			flash('Assignment ' + str(assignment_id) + ', and all related uploaded files and comments have been deleted from the database. Download records have been kept.')
		else:
			flash('There was a problem deleting the assignment.')
		return redirect(url_for('assignments.view_assignments'))
	abort (403)
	
	
############# Peer review forms routes
# Admin page to create new peer review form
@bp.route("/addPeerReviewForm", methods=['GET', 'POST'])
@login_required
def addPeerReviewForm():
	if current_user.is_authenticated and app.models.is_admin(current_user.username):
		# If first form is completed, dynamically generate second form
		if request.form:
			# Remove csrf_token, submit fields to leave only the completed boxes
			formDict = request.form.to_dict()
			del formDict['csrf_token']
			del formDict['submit']
			# Sort dictionary by keys
			sortedDict = json.dumps(formDict, sort_keys=True)
			# Dynamically generate new form for title/label information
			for questionNumber, fieldName in sortedDict:
				if fieldName == 'TextAreaField':
					setattr(FormModel, questionNumber, TextAreaField(label=name, validators=[DataRequired()]))
				elif fieldName == 'BooleanField':
					setattr(FormModel, questionNumber, TextAreaField(label=name, validators=[DataRequired()]))
				elif fieldName == 'StringField':
					setattr(FormModel, questionNumber, TextAreaField(label=name, validators=[DataRequired()]))
				elif fieldName == 'RadioField':
					setattr(FormModel, questionNumber, TextAreaField(label=name, validators=[DataRequired()]))
				FormModel.submit = SubmitField('Next step')
				form = FormModel()
			
		else:
			# Generate dynamic field names
			numberOfFields = 10
			i = 1
			names = []
			while i < numberOfFields:
				names.append('Question ' + str(i))
				i = i+1
			questionTypes = [('StringField', 'StringField'), ('BooleanField', 'BooleanField'), ('RadioField', 'RadioField'), ('TextAreaField', 'TextAreaField')]
			for name in names:
				setattr(FormModel, name, RadioField(label=name, choices=questionTypes))
			FormModel.submit = SubmitField('Next step')
			form = FormModel()
		
		return render_template('assignments/addPeerReviewForm.html', title='Create new peer review form', form=form)
	abort(403)

# Admin page to view classes
@bp.route("/peerReviewFormAdmin")
@login_required
def peerReviewFormAdmin():
	if current_user.is_authenticated and app.models.is_admin(current_user.username):
			classesArray = app.models.selectFromDb(['*'], 'turma')
			return render_template('assignments/class_admin.html', title='Class admin', classesArray = classesArray)
	abort (403)

	