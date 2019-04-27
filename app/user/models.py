from app import db
import app.models, app.email_model
from app.models import Upload, Download, Assignment, User, Comment
from datetime import datetime
from flask_login import current_user
import string, time, datetime, xlrd
from flask import url_for, render_template, redirect, session, flash, request, abort, current_app

def get_total_user_count ():
	# Remove admins?
	return len(User.query.all())

def process_student_excel_spreadsheet (excel_data_file):
	# Get a list of names, student numbers, and email addresses
	excel_workbook = xlrd.open_workbook(file_contents=excel_data_file.read())
	student_info_sheet = excel_workbook.sheet_by_index(0)
	student_info_dict = []
	for row in range(1, student_info_sheet.nrows):    # Iterate through rows, start at 1 to avoid the header row
		student = {}
		student['name'] =  student_info_sheet.cell(row,1).value
		student['student_number'] =  student_info_sheet.cell(row,0).value
		student['email'] =  student_info_sheet.cell(row,7).value
		student['department'] =  student_info_sheet.cell(row,3).value
		student['section'] =  student_info_sheet.cell(row,4).value
		student['phone_number'] =  student_info_sheet.cell(row,5).value
		student_info_dict.append(student)
	return student_info_dict
	

def add_users_from_excel_spreadsheet (user_array, turma_id):
	for student in user_array:
		user = User(username=student['name'], email=student['email'], student_number=student['student_number'], turma_id=turma_id)
		user.set_password(generate_word_password())
		db.session.add(user)
		db.session.commit()
		'''
		# Email student email with password and asking to confirm email.
		subject = "Renmin WorkUp: Confirm your email"
		token = app.email_model.ts.dumps(str(form.email.data), salt=current_app.config["TS_SALT"])
		confirm_url = url_for('user.confirm_email', token=token, _external=True)
		html = render_template('email/activate.html',confirm_url=confirm_url)
		app.email_model.sendEmail (user.email, subject, html)
		'''
	return True
		
	
def check_if_excel_spreadsheet (filename):
	 return '.' in filename and filename.rsplit('.', 1)[1].lower() in ['xls']
	
############ Password generator
def roll_dice (number_of_dice = 5):
	while True:
		dice_roll = ''
		
		# Roll the dice x number_of_times
		for d in range(number_of_dice):
			dice_roll = dice_roll + str(random.choice(list(range(6))))
			
		# Check the combination connects to a word in the list
		word = add_to_word_list (dice_roll)
		if word != False:
			return word

def add_to_word_list (dice_roll):
	searchfile = open("eff_large_wordlist.txt", "r")
	
	for line in searchfile:
		if dice_roll in line:
			word = line[6:]
			searchfile.close()
			return word
	searchfile.close()
	return False

def generate_word_password (number_of_words = 4):
	password = ''
	
	for i in range(number_of_words):
		password = password + roll_dice ()
		
	generated_password = "-".join(password.splitlines())
	return generated_password
			
##########################