from app import db

from app.models import Assignment, Upload, User
from app.assignments.models import AssignmentGrade
from app.classes.models import get_class_enrollment_from_class_id

import json

# Model to add an entry to the Gradebook
# Can either be a standalone entry (i.e., title + grade), or connected to an assignment (i.e. linked_assignment -> linked_asignment_grade)
class GradebookEntry (db.Model):
	id = db.Column(db.Integer, primary_key=True)
	turma_id = db.Column(db.Integer, db.ForeignKey('turma.id'))
	linked_assignment = db.Column(db.Integer, db.ForeignKey('assignment.id'))
	title = db.Column(db.String(500))
	date = db.Column(db.Date)
	combined_weight = db.Column(db.Float)

	def add (self):
		db.session.add(self)
		db.session.commit()



# Model to save the distribution of gradebook percentrages
'''
percentages = [
	{
		grouped_weight: 30,
		gradebook_entries: 
		[
			{gradebook_entry_id: 1, weight: 45}
			{gradebook_entry_id: 5, weight: 55}
		]
	},

	{
		grouped_weight: 70,
		gradebook_entries: 
		[
			{gradebook_entry_id: 2, weight: 20}
			{gradebook_entry_id: 4, weight: 80}
		]
	}
]
'''
class GradebookPercentages (db.Model):
	id = db.Column(db.Integer, primary_key=True)
	turma_id = db.Column(db.Integer, db.ForeignKey('turma.id'))
	percentages = db.Column(db.String(5000))

	def add (self):
		db.session.add(self)
		db.session.commit()


# A Gradebook Grade entry. Used for recording standalone gradebook entries
class GradebookGrade (db.Model):
	id = db.Column(db.Integer, primary_key=True)
	gradebook_entry_id = db.Column(db.Integer, db.ForeignKey('gradebook_entry.id')) 
	grade = db.Column(db.Float)
	student_id = db.Column(db.Integer, db.ForeignKey('user.id'))

	def add (self):
		db.session.add(self)
		db.session.commit()


# Save a gradebook grade. This will overwrite any existing grade
def save_gradebook_grade (student_id, gradebook_entry_id, grade):
	existing_grade = GradebookGrade.query.filter_by (student_id = student_id, gradebook_entry_id = gradebook_entry_id).first()

	if existing_grade is not None:
		existing_grade.grade = grade
		db.session.commit ()
	
	else:
		gradebook_grade = GradebookGrade (
			gradebook_entry_id = gradebook_entry_id,
			student_id = student_id,
			grade = grade
		)
		gradebook_grade.add ()


# Save a gradebook percentage object. This will overwrite any existing object
def save_gradebook_percentage_object (turma_id, percentage_object):
	existing_percentage_object = GradebookPercentages.query.filter_by(turma_id = turma_id).first()

	if existing_percentage_object is not None:
		existing_percentage_object.percentages = json.dumps (percentage_object)
		db.session.commit()
	
	else:
		percentage_object = GradebookPercentages (
			turma_id = turma_id,
			percentages = json.dumps (percentage_object)
		)
		percentage_object.add()


# Get a formatted object containing all assessment criteria for a class
def get_assessment_criteria_from_class_id (turma_id):
	assessment_criteria = []
	
	# Get all the different assessment points for this class
	for assessment_type in GradebookEntry.query.filter_by(turma_id = turma_id):
		assessment_criteria.append (get_assessment_criteria_object(assessment_type.id))
	
	return assessment_criteria


# Get a formatted object containing the information for an assessment_type
def get_assessment_criteria_object (gradebook_entry_id):
	assessment = GradebookEntry.query.get (gradebook_entry_id)
	
	# If this is a linked assignment:
	if assessment.linked_assignment != None: 
	
		# Get the assignment information
		assignment = Assignment.query.get(assessment.linked_assignment)
		return {
			'gradebook_entry': assessment,
			'assessment_type': 'linked_assignment',
			'assessment': assignment
		}
	
	# Otherwise link the entry
	else:
		return {
			'gradebook_entry': assessment,
			'assessment_type': 'standalone_assessment',
			'assessment': assessment
		}



# Function to return a complete class gradebook
# This will contain an array of students, and each student will have several objects representing the assessment criteria
# Supplying an optional student_id will limit the returned result to that student
def get_class_gradebook (turma_id, student_id = False):
	students = []
	assessment_criteria = get_assessment_criteria_from_class_id (turma_id)

	# If we are supplying a user_id, i.e., single student return mode
	if student_id :
		user_dict = User.query.get (student_id).__dict__
		user_dict['grades'] = []
		students.append (user_dict)

	# Compile a list of all the students in the class
	else:
		for enrollment_ignored, turma_ignored, user in get_class_enrollment_from_class_id (turma_id):
			user_dict = user.__dict__
			user_dict['grades'] = []
			students.append (user_dict) # Convert db Object to a dictionary at this point, so we can add additional criteria
		
	# Loop through each student and add their assessment criteria
	for student in students:
		for assessment in assessment_criteria:
			
			# If this type is an assignment
			if hasattr(assessment['assessment'], 'assignment_task_file_id'):

				# Get the grade for each student
				# Grades are stored by upload_id, grade, user_id. 
				# So check if a user has submitted an upload for the assignment, then check for grade
				upload = Upload.query.filter_by(assignment_id = assessment['assessment'].id).filter_by(user_id = student['id']).first()

				# Fill out the grades
				try:
					grade = AssignmentGrade.query.filter_by(upload_id = upload.id).first()
				except: # i.e., upload was None, and has no ID
					grade = None
					
				student['grades'].append ({
					'grade': grade.grade if grade is not None else 'N/A',
					'is_linked_assignment': True, 
					'gradebook_entry': assessment['gradebook_entry'],
					'assessment_id': assessment['assessment'].id,
					'upload_id': upload.id if upload is not None else None
				})

			# If this assignment is a standalone assignment
			else: 
				
				# Get the standalone grade
				grade = GradebookGrade.query.filter_by(student_id=student['id']).filter_by(gradebook_entry_id=assessment['assessment'].id).first()
				student['grades'].append ({
					'grade': grade.grade if grade is not None else 'N/A',
					'is_linked_assignment': False, 
					'gradebook_entry': assessment['gradebook_entry'],
					'assessment_id': assessment['assessment'].id
				})
						
	return students

# Function to remove a linked assignment from a class gradebook
def remove_linked_assignment_from_gradebook (turma_id, assignment_id):
	# Remove the DB entry
	gradebook_entry = GradebookEntry.query.filter_by(turma_id = turma_id).filter_by(linked_assignment= assignment_id).first()
	if gradebook_entry is not None:
		db.session.delete(gradebook_entry)
		db.session.commit()

	# Remove this from the class percentage table (how to adjust?)
