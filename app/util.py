from app import workUpApp

def sendEmail (to, subject, text):
	import smtplib
	
	FROM = workUpApp.config['SMTP_FROM_ADDRESS']
	TO = [str(to)]
	SUBJECT = str(subject)
	TEXT = str(text)
	
	# Prepare actual message
	message = """\
	From: %s
	To: %s
	Subject: %s
	
	%s
	""" % (FROM, ", ".join(TO), SUBJECT, TEXT)
	
	# Send the mail
	s = smtplib.SMTP(workUpApp.config['SMTP_SERVER'],workUpApp.config['SMTP_PORT'])
	s.ehlo()
	s.starttls()
	s.ehlo()
	s.login(workUpApp.config['SMTP_USERNAME'], workUpApp.config['SMTP_PASSWORD'])
	s.sendmail(FROM, TO, message)
	s.quit()