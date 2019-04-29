from flask import current_app
from itsdangerous import URLSafeTimedSerializer

import smtplib
import email.message

ts = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])

def send_email (to, subject, text):
	msg = email.message.Message()
	
	msg['From'] = current_app.config['SMTP_FROM_ADDRESS']
	msg['To'] = str(to)
	msg['Subject'] = str(subject)
	msg.add_header('Content-Type','text/html')
	msg.set_payload (str(text))
	
	# Send the mail
	s = smtplib.SMTP(current_app.config['SMTP_SERVER'],current_app.config['SMTP_PORT'])
	s.ehlo()
	s.starttls()
	s.ehlo()
	s.login(current_app.config['SMTP_USERNAME'], current_app.config['SMTP_PASSWORD'])
	s.sendmail(msg['From'], msg['To'], msg.as_string())
	s.quit()