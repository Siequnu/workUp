from app import workUpApp
from itsdangerous import URLSafeTimedSerializer

import smtplib
import email.message

ts = URLSafeTimedSerializer(workUpApp.config["SECRET_KEY"])

def sendEmail (to, subject, text):
	msg = email.message.Message()
	
	msg['From'] = workUpApp.config['SMTP_FROM_ADDRESS']
	msg['To'] = str(to)
	msg['Subject'] = str(subject)
	msg.add_header('Content-Type','text/html')
	msg.set_payload (str(text))
	
	# Send the mail
	s = smtplib.SMTP(workUpApp.config['SMTP_SERVER'],workUpApp.config['SMTP_PORT'])
	s.ehlo()
	s.starttls()
	s.ehlo()
	s.login(workUpApp.config['SMTP_USERNAME'], workUpApp.config['SMTP_PASSWORD'])
	s.sendmail(msg['From'], msg['To'], msg.as_string())
	s.quit()