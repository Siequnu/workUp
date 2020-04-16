from flask_marshmallow import Marshmallow
from app.models import LibraryUpload
from app import ma

class LibraryUploadSchema (ma.SQLAlchemySchema):
	class Meta:
		fields = ('id', 'title', 'description', 'filename')