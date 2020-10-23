from flask import render_template, flash, abort, redirect, url_for
from flask_login import current_user, login_required

from . import bp
from .models import GradebookEntry

import app.models 
from app.models import Assignment, Turma


# Gradebook index
@bp.route("/")
@bp.route("/<int:turma_id>")
@login_required
def gradebook_index(turma_id = False):
	if app.models.is_admin(current_user.username):
		classes = app.classes.models.get_teacher_classes_from_teacher_id (current_user.id)
		turma_choices = [(turma.id, turma.turma_label) for turma in classes]
		
		# If we are accessing a specific class
		if turma_id:
			turma = Turma.query.get(turma_id)
			
			if turma is None: abort (404)
			if app.classes.models.check_if_turma_id_belongs_to_a_teacher (turma_id, current_user.id) is False: abort (403)	
			
			assignments = app.assignments.models.get_assignments_from_turma_id (turma.id)

			gradebook_entries = GradebookEntry.query.filter_by (turma_id = turma.id)

			return render_template (
				'gradebook_index.html',
				turma_choices = turma_choices,
				turma = turma,
				assignments = assignments,
				gradebook_entries = gradebook_entries
			)
		
		# Accessing the main page, i.e., no class selected yet
		else:
			return render_template (
				'gradebook_index.html',
				turma_choices = turma_choices,
			)

# Route to associate an assignment with a gradebook
@bp.route("/<int:turma_id>/link/assignment/<int:assignment_id>")
@login_required
def link_assigment_to_gradebook(turma_id, assignment_id):
	if app.models.is_admin(current_user.username):
		turma = Turma.query.get(turma_id)
		if turma is None: abort (403)
		
		if app.classes.models.check_if_turma_id_belongs_to_a_teacher (turma_id, current_user.id) is False:
			abort (403)	

		new_gradebook_entry = GradebookEntry (
			turma_id = turma_id,
			linked_assignment = assignment_id
		)
		new_gradebook_entry.add()

		flash ('New assignment linked successfully', 'success')
		return redirect (url_for('gradebook.gradebook_index', turma_id = turma_id))
		

@bp.route("/create/template")
@login_required
def create_gradebook_template():
	if app.models.is_admin(current_user.username):
		#¡# Shuld check for turmas, and compile: current a TA won't get any assignments showing
		all_assignments = Assignment.query.filter_by(created_by_id = current_user.id).all()
		return render_template (
			'create_gradebook_template.html',
			all_assignments = all_assignments)