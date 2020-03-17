from flask import Blueprint

bp = Blueprint('grammar', __name__)

from app.grammar import routes, forms, models