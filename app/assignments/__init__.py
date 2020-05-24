from flask import Blueprint

bp = Blueprint('assignments', __name__, template_folder='templates')

from app.assignments import routes, models, forms