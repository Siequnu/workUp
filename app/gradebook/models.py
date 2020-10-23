from app import db

class GradebookEntry (db.Model):
	id = db.Column(db.Integer, primary_key=True)
	turma_id = db.Column(db.Integer, db.ForeignKey('turma.id'))
	linked_assignment = db.Column(db.Integer, db.ForeignKey('assignment.id'))
	title = db.Column(db.String(500))

	def add (self):
		db.session.add(self)
		db.session.commit()