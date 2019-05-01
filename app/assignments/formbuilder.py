#!/usr/bin/env python

import re
import json

class formLoader:
	
	def __init__(self, form_json, form_action, submit_label = 'Submit', data_array = False):
		self.form_data = json.loads(form_json.replace('\\', ''))
		self.action = form_action
		self.submit_label = str(submit_label)
		self.data_array = data_array

	def render_form(self):
		"""
		Render Form
		"""
		if (not self.form_data or not self.action):
			return False

		fields = '' 

		for field in self.form_data['fields']:

			if field['type'] == 'element-single-line-text':
				fields += self.element_single_line_text(field)

			if field['type'] == 'element-number':
				fields += self.element_number(field)

			if field['type'] == 'element-paragraph-text':
				fields += self.element_paragraph_text(field)

			if field['type'] == 'element-checkboxes':
				fields += self.element_checkboxes(field)

			if field['type'] == 'element-multiple-choice':
				fields += self.element_multiple_choice(field)

			if field['type'] == 'element-dropdown':
				fields += self.element_dropdown(field)

			if field['type'] == 'element-section-break':
				fields += self.element_section_break(field)

		form = self.open_form(fields)

		return form

	def open_form(self, fields):
		"""
		Render the form header
		"""
		html = '''<form action="{0}" method="post" accept-charset="utf-8" role="form" novalidate="novalidate" >'''.format(self.action);
		html += '''<div class="form-title">'''
		html += '''<h2>{0}</h2><h3>{1}</h3>'''.format(self.form_data['title'], self.form_data['description'])
		html += fields
		html += '''<button type="submit" class="btn btn-primary">{0}</button>'''.format(self.submit_label)
		html += '''</div></form>'''

		return html

	def encode_element_title(self, title):
		"""
		Encode Element Title
		"""
		clean_string = re.compile(r"[^a-zA-Z0-9.-_]")

		string = title.lower().replace(' ', '_')
		string = re.sub(clean_string, '', string)

		return string

	def make_label(self, id, title, required):
		"""
		Get formatted label for form element
		"""
		if required:
			html = '''<label for="{0}">{1} <span style="color: red">*</span></label>'''.format(id, title)
		else:
			html = '''<label for="{0}">{1} </label>'''.format(id, title)

		return html
	
	def get_text_element_data (self, id):
		if self.data_array is not False:
			if id in self.data_array:
				return self.data_array[id]		
		return ''
	
	def get_select_multiple_checked_choice (self, id, choice):
		if self.data_array is not False:
			if id in self.data_array:
				if self.data_array[id] == choice:
					return 'checked'
		return ''
	
	def element_single_line_text(self, field):
		"""
		Render single line text
		"""
		id = self.encode_element_title(field['title'])
		required = 'required' if field['required'] else False
			
		html = '''<div class="form-group">'''
		html += self.make_label(id, field['title'], required)
		html += '''<input type="text" name="{0}" id="{0}" value="{2}" class="form-control {1}">'''.format(id, required, self.get_text_element_data(id))
		html += '''</div>'''

		return html

	def element_number(self, field):
		"""
		Render number
		"""
		id = self.encode_element_title(field['title'])
		required = 'required' if field['required'] else False

		html = '''<div class="form-group">'''
		html += self.make_label(id, field['title'], required)
		html += '''<input type="number" name="{0}" value="{2}" id="{0}" class="form-control {1}">'''.format(id,
																											required,
																											self.get_text_element_data(id))
		html += '''</div>'''

		return html

	def element_paragraph_text(self, field):
		"""
		Render paragraph text
		"""
		id = self.encode_element_title(field['title'])
		required = 'required' if field['required'] else False

		html = '''<div class="form-group">'''
		html += self.make_label(id, field['title'], required)
		html += '''<textarea id="{0}" name="{0}" class="form-control {1}" rows="3">{2}</textarea>'''.format(id,
																													 required,
																													 self.get_text_element_data(id))
		html += '''</div>'''

		return html

	def element_checkboxes(self, field):
		"""
		Render checkboxes
		"""
		id = self.encode_element_title(field['title'])
		required = 'required' if field['required'] else False

		html = '''<div class="form-group">'''
		html += self.make_label(id, field['title'], required)

		for i in range(len(field['choices'])):
			field_name = "{0}_{1}".format(id, i)
			html += '''<div class="checkbox"><label>'''
			html += '''<input type="checkbox" name="{0}_{1}" id="{0}-{1}" value="{2}" {3}>{4}'''.format(id,
																										i,
																										field['choices'][i]['value'],
																										self.get_select_multiple_checked_choice(field_name, field['choices'][i]['value']),
																										field['choices'][i]['title'])
			html += '''</label></div>'''
			

		html += '''</div>'''
		
		return html

	def element_multiple_choice(self, field):
		"""
		Render multiple choice
		"""
		id = self.encode_element_title(field['title'])
		required = 'required' if field['required'] else False

		html = '''<div class="form-group">'''
		html += self.make_label(id, field['title'], required)

		for i in range(len(field['choices'])):
			checked = self.get_select_multiple_checked_choice(id, field['choices'][i]['value'])
			
			html += '''<div class="radio"><label>'''
			html += '''<input type="radio" name="{0}" id="{0}_{1}" value="{2}" {3}>{4}'''.format(id, i, field['choices'][i]['value'], checked, field['choices'][i]['title'])
			html += '''</label></div>'''

		html += '''</div>'''

		return html

	def element_dropdown(self, field):
		"""
		Render dropdown
		"""
		id = self.encode_element_title(field['title'])
		required = 'required' if field['required'] else False

		html = '''<div class="form-group">'''
		html += self.make_label(id, field['title'], required)
		html += '''<select name="{0}" id="{0}" class="form-control {1}">'''.format(id, required)

		for choice in field['choices']:
			checked = self.get_select_multiple_checked_choice(id, field['choices'][i]['value'])
			html += '''<option value="{0}" {1}>{2}</option>'''.format(choice['value'], checked, choice['title'])

		html += '</select></div>'

	def element_section_break(self, field):
		html = '''<div class="form-group section-break">'''
		html += '''<hr/><h4>{0}</h4><p>{1}</p>'''.format(field['title'], field['description'])
		html += '''</div>'''

		return html