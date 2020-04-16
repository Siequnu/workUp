from flask import Blueprint
from flask_restful import Api

bp = Blueprint('api', __name__)
api = Api (bp)

from app.api import routes, schemas

api.add_resource(routes.LibraryListApi, '/api/v1/library')
api.add_resource(routes.LibraryUploadApi, '/api/v1/library/<int:id>')