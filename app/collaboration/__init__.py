from flask import Blueprint

bp = Blueprint('collaboration', __name__)

from app.collaboration import routes