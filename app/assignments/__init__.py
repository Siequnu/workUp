from flask import Blueprint

bp = Blueprint('assignments', __name__)

from app.assignments import routes, models