workUp is a app web application designed to help teachers distribute student work for peer review.

The site works as a simple upload interface, whereby uploaded works are automatically redistributed amongst the uploadees.

Uploaded files are tagged with a student number, so that the student never receives their own work back.

Future plans are:
	- Develop a database system to track files
	- Student log-in feature where they can access information on their uploads
	- Log to track which files were delivered for peer review to which students

workUp has the following main dependencies:
-python >= 2.7
-libapache2-mod-wsgi 
-python-dev
-pip:
	Flask 
	flask_httpauth		authentication handler
	flask-wtf		for handling of web form ! See NB below regarding flask-wtf rendering of labels in RadioFields
	flask-login		log-in handler
	flask-sqlalchemy	database backend
	flask-migrate		database backend
	flask-bootstrap		css theme
	flask_sslify		maintain ssl connections
	flask-moment		wrapper for Moment.js

Please see the complete list in requirements.txt

Deployment:
	- If using wsgi_mod with apache ensure that WSGIPassAuthorization is set to On in the .htaccess file
	- Setup server specific config in config.py
	- Ensure static/uploads/ folder is readable by apache (ie. sudo chown www-data)
	
Flask-wtf NB:
https://stackoverflow.com/questions/27705968/flask-wtform-radiofield-label-does-not-render
It might be intended by the author of "quick_form" macro, or more likely he/she missed a line of code to render out the label of RadioField, as the same is done for other types of fields.
To hack it, locate the file "bootstrap/wtf.html", where macro "quick_form" is defined.
add this line:

{{field.label(class="control-label")|safe}}

before the "for" loop:

{% for item in field -%}
  <div class="radio">
    <label>
      {{item|safe}} {{item.label.text|safe}}
    </label>
  </div>
{% endfor %}
Hope this works for you.
