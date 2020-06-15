from flask import current_app
import datetime

# Returns a string with the correct greeting based on the time of the day
def get_greeting ():
	# Get the greeting
	if datetime.datetime.now().hour < 12:
		return 'Good morning'
	elif 12 <= datetime.datetime.now().hour < 18:
		return 'Good afternoon'
	else:
		return 'Good evening'

# Checks if a service is enabled and returns true or false
def is_active_service (service_name):
	for service in current_app.config['CUSTOM_SERVICES']:
		if str(service_name) in service.values():
			return True
	return False