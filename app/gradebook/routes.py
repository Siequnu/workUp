from flask import render_template, flash, abort, redirect, url_for, jsonify, request
from flask_login import current_user, login_required

from . import bp
from .models import GradebookEntry, get_assessment_criteria_from_class_id, save_gradebook_grade
from .forms import AssessmentCriteriaForm

import app.models 
from app.models import Assignment, Turma
from app.classes.models import check_if_student_is_in_teachers_class 


# Admin API route to save a user's grade
@bp.route("/api/grade/save/<int:student_id>/<gradebook_entry_id>", methods=['POST'])
@login_required
def api_save_gradebook_grade(student_id, gradebook_entry_id):
	if app.models.is_admin(current_user.username):
		if check_if_student_is_in_teachers_class (student_id, current_user.id):
			
			grade = request.json.get('grade')

			save_gradebook_grade(student_id, gradebook_entry_id, grade)

			return jsonify({'success': 'Grade added successfully'})
			
		return jsonify({'error': 'This student is not registered in your class.'})
	abort(403)


# Gradebook index
# This route shows both a main page (if no turma_id is given), or the class info for a turma
@bp.route("/")
@bp.route("/<int:turma_id>")
@login_required
def gradebook_index(turma_id = False):
	if app.models.is_admin(current_user.username):
		classes = app.classes.models.get_teacher_classes_from_teacher_id (current_user.id)
		turma_choices = [(turma.id, turma.turma_label) for turma in classes]
		
		# If we are accessing a specific class
		if turma_id:
			
			# Get the turma
			turma = Turma.query.get(turma_id)
			if turma is None: abort (404)
			
			# Security check: is this this teacher's class?
			if app.classes.models.check_if_turma_id_belongs_to_a_teacher (turma_id, current_user.id) is False: abort (403)	
			
			# Get additional info
			assignments = app.assignments.models.get_assignments_from_turma_id (turma.id)
			assessment_criteria = app.gradebook.models.get_assessment_criteria_from_class_id (turma_id)
			gradebook = app.gradebook.models.get_class_gradebook (turma.id) # i.e. students and each assignment

			# Get the Assessment Criteria form, which will be used in a modal
			form = AssessmentCriteriaForm ()

			return render_template (
				
				'gradebook_index.html',
				turma_choices = turma_choices,

				turma = turma,
				assignments = assignments,
				gradebook = gradebook,
				assessment_criteria = assessment_criteria,
				
				form = form
			)
		
		# Accessing the main page, i.e., no class selected yet
		else:
			return render_template (
				'gradebook_index.html',
				turma_choices = turma_choices,
			)


# Route to create a new assessment criteria for a class
@bp.route("/criteria/add/<int:turma_id>", methods = ['POST'])
@login_required
def create_new_assignment_criteria_for_class(turma_id):
	form = AssessmentCriteriaForm ()
	if app.models.is_admin(current_user.username):
		if form.validate_on_submit():
			
			# Get the class
			turma = Turma.query.get(turma_id)
			if turma is None: abort (404)
			
			# Security check
			if app.classes.models.check_if_turma_id_belongs_to_a_teacher (turma_id, current_user.id) is False:
				abort (403)	

			# Create the new assessment criteria
			new_gradebook_entry = GradebookEntry (
				turma_id = turma_id,
				title = form.title.data,
				date = form.date.data
			)
			new_gradebook_entry.add()

			# Display confirmation message and redirect
			flash ('New criteria added successfully', 'success')
			return redirect (url_for('gradebook.gradebook_index', turma_id = turma.id))

		else:
			abort (404)
	else:
		abort (404)




# Route to associate an assignment with a gradebook
@bp.route("/<int:turma_id>/link/assignment/<int:assignment_id>")
@login_required
def link_assigment_to_gradebook(turma_id, assignment_id):
	if app.models.is_admin(current_user.username):
		turma = Turma.query.get(turma_id)
		if turma is None: abort (403)
		
		if app.classes.models.check_if_turma_id_belongs_to_a_teacher (turma_id, current_user.id) is False:
			abort (403)	

		# Check to see if we already have this assignment associated to this class
		if GradebookEntry.query.filter_by(turma_id = turma_id).filter_by(linked_assignment = assignment_id).first() is not None:
			flash ('This assignment has already been linked to this class.', 'info')
			return redirect (url_for('gradebook.gradebook_index', turma_id = turma_id))

		# Add a new DB entry
		new_gradebook_entry = GradebookEntry (
			turma_id = turma_id,
			linked_assignment = assignment_id
		)
		new_gradebook_entry.add()

		# Display a success message and redirect to the class gradebook page
		flash ('New assignment linked successfully', 'success')
		return redirect (url_for('gradebook.gradebook_index', turma_id = turma_id))
		