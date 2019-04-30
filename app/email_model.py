from flask import current_app

from itsdangerous import URLSafeTimedSerializer
ts = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])

from flask_mail import Message
from app import mail

def send_email (to, subject, text):
	msg = Message(subject, recipients = to.split())
	msg.html = text
	mail.send(msg)