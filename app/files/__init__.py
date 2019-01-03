from flask import Blueprint

bp = Blueprint('files', __name__)

from app.files import routes, models