import datetime

# Returns a string with the correct greeting based on the time of the day
def get_greeting ():
	# Get the greeting
	if datetime.datetime.now().hour < 12:
		return 'Good morning'
	elif 12 <= currentTime.hour < 18:
		return 'Good afternoon'
	else:
		return 'Good evening'