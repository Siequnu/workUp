# workUp
workUp is a app web application designed to help teachers distribute student work for peer review.

Managing student work for peer distribution is time consuming and can be a large impediment to
teachers implementing this otherwise very beneficial study method. It is hoped that this app can
assist lecturers in implementing peer-review in their classes.

## Literature Review

Despite the overwhelming research in support of peer review as an educational tool (Liu, Psyarchik & Taylor, 2002; Brammer & Rees, 2007; Graff, 2009)
it remains to be implemented in many classrooms. One cause of this is time constraints, and the inherently time consuming nature of peer-review (Crowe, Silva & Ceresola, 2015).

One solution to this is the use of peer-review software to automate administrative tasks inherent to peer review. While [comparative studies](https://www.reap.ac.uk/PEER/Software.aspx) have
been made, most software for this purpose is expensive, and suitable only for large-scale deployment at a University- or College- level. Sofwares like **Aropa**, **Calibrated Peer Review**,
**PeerMark (TURNITIN)**, and **PRAZE** are hard to set-up, resource-intensive to run and require a large amount of commitement and computer knowledge from education practitioners.

workUp is an attempt to make a software that:

* provides simple deployment that can be achieved by any university lecturer,

* provides a clear and easy to use student- and admin-facing interface.

## How It Works

The site works as a simple upload interface, whereby uploaded works are automatically
redistributed amongst the uploadees.

Uploaded files are tagged with a student number, so that the student never receives
their own work back.

Students can log-in to view their assignments, and once an assignment has been upload, the student
can submit peer reviews for two other assignments. These peer reviews are guided through a feedback form,
although as students get more comfortable in providing feedback, progressively less guided forms can be
given to students.

## Deployment

* This git can be cloned onto a deployment server. A suggested location is `/var/www/`.
```sh
$ cd /var/www
$ git clone https://github.com/Siequnu/workUp.git
```

* `config.py.sample` should be cp to `config.py` and the administration sign-up codes filled in.

* Install and enable mod_wsgi:
```sh
$ sudo apt-get install libapache2-mod-wsgi python-dev
$ sudo a2enmod wsgi 
```

* a workUp.wsgi file should be created in `/PATH_TO_WORKUP_ROOT/workUp`. Adjust the **PATH_WORK_WORKUP_ROOT** variable in `sys.path.insert`
and add a secret `application.secret_key`.

```sh
#!/usr/bin/python
import sys
import logging
logging.basicConfig(stream=sys.stderr)
sys.path.insert(0,"/PATH_TO_WORKUP_ROOT/workUp/")

from app import workUpApp as application
application.secret_key = *************
```

* in `/etc/apache2/sites-available` create a file called `workUp.conf` based on the template below. Customise the
**SERVER_WEB_NAME**, **SERVER_ADMIN_EMAIL**, **PATH_TO_WORKUP_ROOT**, **SERVER_NAME**,
 and **SERVER_NAME** variables. Leave **SERVER_NAME** and **REQUEST_URI** unmodified in
 `RewriteCond` and `RewriteRule`

```sh
<VirtualHost *:80>
                ServerName SERVER_WEB_NAME
                ServerAdmin SERVER_ADMIN_EMAIL
                WSGIScriptAlias / /PATH_TO_WORKUP_ROOT/workUp/workUp.wsgi
                <Directory /PATH_TO_WORKUP_ROOT/workUp/app/>
                        Order allow,deny
                        Allow from all
                </Directory>
                Alias /static /PATH_TO_WORKUP_ROOT/app/static
                <Directory /PATH_TO_WORKUP_ROOT/app/static/>
                        Order allow,deny
                        Allow from all
                </Directory>
                ErrorLog /PATH_TO_WORKUP_ROOT/logs/error.log
                LogLevel warn
                CustomLog /PATH_TO_WORKUP_ROOT/logs/access.log combined
RewriteEngine on
RewriteCond %{SERVER_NAME} = SERVER_WEB_NAME
RewriteRule ^ https://%{SERVER_NAME}%{REQUEST_URI} [END,NE,R=permanent]
</VirtualHost>
```

* Enable the virtual host with the following command:

```sh
$ sudo a2ensite workUp
```

* SSL certification can be obtained for free using the [Certbot ACME client](https://certbot.eff.org)

* pip is used to install Flask. If pip is not installed, install it on Ubuntu through apt-get.
This can be installed globally rather than in a virtualenv to facilitate setup.
Install the complete requirements list from requirements.txt

```sh
$ sudo apt-get install python-pip 
$ sudo pip install Flask 
$ pip install -r /path/to/requirements.txt
```

* The initial database should be generated by using `flask db init`, `flask db migrate` and finally `flask db commit` to generate tables from the `models.py` page.

* After set-up, restart Apache using `sudo service apache2 restart`

## Deployment notes

* If using **libapache2-mod-wsgi** (`wsgi_mod`) with apache ensure that **WSGIPassAuthorization** is set to `On` in the `.htaccess` file

* Setup server specific config in `config.py`

* Ensure `/static/uploads/` folder is readable by apache:

```sh
$ sudo chown -R www-data static/uploads
```


## Dependencies

The following third-party libraries are used:

`Flask`: common package to write Python web apps;

`flask_httpauth`: authentication handler

`flask-wtf`: handling web forms

`flask-login`: log-in and session manager

`flask-sqlalchemy`: database backend

`flask-migrate`: update databases on deployment servers

`flask-bootstrap`: css theme

`flask-sslify`: maintain and force secure connections

## Deployment notes

There is a bug in the **Flask-wtf** library, whereby Flask wtf form radio-button labels do not render.

This issue is discussed at length [on Stackoverflow](https://stackoverflow.com/questions/27705968/flask-wtform-radiofield-label-does-not-render)


>It might be intended by the author of "quick_form" macro, or more likely he/she missed a
>line of code to render out the label of RadioField, as the same is done for other types of fields.

The proposed solution is:

> To hack it, locate the file `bootstrap/wtf.html`, where macro `quick_form` is defined.
> Add this line:

```sh
{{field.label(class="control-label")|safe}}

before the "for" loop:

{% for item in field -%}
  <div class="radio">
    <label>
      {{item|safe}} {{item.label.text|safe}}
    </label>
  </div>
{% endfor %}
```