from flask import current_app
from app import db
from app.models import GrammarCheck
import app.models

# Delete all records of a grammar check
def delete_all_grammar_check_records_from_user_id(user_id):
	checks = GrammarCheck.query.filter_by(user_id=user_id).all()
	if checks is not None:
		for check in checks:
			db.session.delete(check)
	db.session.commit()
