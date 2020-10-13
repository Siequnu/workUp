from flask import render_template, flash, abort, redirect, url_for
from flask_login import current_user, login_required

from . import bp

import app.models 
from app.models import Assignment

from datetime import datetime


# Live assessment index
@bp.route("/")
@login_required
def gradebook_index():
	if app.models.is_admin(current_user.username):
		return render_template (
			'gradebook_index.html',
			)

@bp.route("/create/template")
@login_required
def create_gradebook_template():
	if app.models.is_admin(current_user.username):
		#¡# Shuld check for turmas, and compile: current a TA won't get any assignments showing
		all_assignments = Assignment.query.filter_by(created_by_id = current_user.id).all()
		return render_template (
			'create_gradebook_template.html',
			all_assignments = all_assignments)