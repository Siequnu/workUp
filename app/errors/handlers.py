from flask import render_template
from app import workUpApp, db

@workUpApp.errorhandler(403)
def access_denied(error):
    return render_template('errors/403.html'), 403

@workUpApp.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@workUpApp.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('errors/500.html'), 500