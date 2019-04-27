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
**PeerMark (TURNITIN)**, and **PRAZE** are hard to set-up, resource-intensive to run and require a large amount of commitment and computer knowledge from education practitioners.

workUp is an attempt to make a software that:

* provides simple deployment that can be achieved by any university lecturer,

* provides a clear and easy to use student- and admin-facing interface.

![View assignments](https://raw.githubusercontent.com/Siequnu/workUp/master/assets/view_assignments.png)

## How It Works

The site works as a simple upload interface, whereby uploaded works are automatically
redistributed amongst the uploadees.

Uploaded files are tagged with a student number, so that the student never receives
their own work back.

Students can log-in to view their assignments, and once an assignment has been upload, the student
can submit peer reviews for two other assignments. These peer reviews are guided through a feedback form,
although as students get more comfortable in providing feedback, progressively less guided forms can be
given to students.
![Submit peer review](https://raw.githubusercontent.com/Siequnu/workUp/master/assets/submit_peerreview.png)


## Deployment

* Update the server

```sh
sudo apt-get update && sudo apt-get upgrade
sudo apt install screen
```

* Change from root user to newly created ubuntu account
```sh
$ adduser --gecos "" ubuntu
$ usermod -aG sudo ubuntu
$ su ubuntu
```

* Passwordless login.

On local machine check contents of directory ~.ssh as follows:
```sh
$ ls ~/.ssh
id_rsa  id_rsa.pub
```
The directory should show id_rsa and ir_rsa.pub. If not, you can create the files by running $ ssh-keygen.
You now need to configure your public key as an authorized host in your server.
On the terminal that you opened on your own computer, print your public key to the screen:

```sh
$ cat ~/.ssh/id_rsa.pub
ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQCjw....F8Xv4f/0+7WT miguel@miguelspc
```

This is going to be a very long sequence of characters, possibly spanning multiple lines. You need to copy this data to the clipboard, and then switch back to the terminal on your remote server, where you will issue these commands to store the public key:

```sh
$ mkdir ~/.ssh
$ echo <paste-your-key-here> >> ~/.ssh/authorized_keys
$ chmod 600 ~/.ssh/authorized_keys
```

Check this is working with the following command. No password should be needed.
```sh
$ ssh ubuntu@<server-ip-address>
```

* Securing the server. Edit `/etc/ssh/sshd_config` and change
```
PermitRootLogin no
PasswordAuthentication no
```

Then restart ssh with `sudo service ssh restart`

* Installing a firewall
```sh
$ sudo apt-get install -y ufw
$ sudo ufw allow ssh
$ sudo ufw allow http
$ sudo ufw allow 443/tcp
$ sudo ufw --force enable
$ sudo ufw status
```

* Install base dependencies
```sh
$ sudo apt-get -y update
$ sudo apt-get -y install python3 python3-venv python3-dev supervisor nginx git 
```

* Install extra dependencies. Gunicorn is used to run flask, libmagickwand-dev is used to process thumbnails.
```sh
$ sudo apt-get -y install gunicorn libmagickwand-dev
```

* Installing the source code
```sh
$ cd ~
$ git clone https://github.com/Siequnu/workUp.git
$ cd workUp
$ python3 -m venv venv
$ source venv/bin/activate
$ pip install -r requirements.txt
$ pip install gunicorn
```

* Create a .env file with environmental variables. Generate a UUID with `python3 -c "import uuid; print(uuid.uuid4().hex)"`
```
SECRET_KEY=52cb883e323b48d78a0a36e8e951ba4a
```

```sh
$ echo "export FLASK_APP=workup.py" >> ~/.profile
```

* Setup local config by copying the sample file and renaming it to `config.py`

* Setup database with
```sh
$ flask db init
$ flask db migrate
$ flask db upgrade
```

This should run without any errors. Create an admin in the new database
```sh
$ python3 create_admin
```

* The program should now be able to run via the following command.
The last two variables are the name of the .py script
that runs the program, and the name of the app folder.
```
$ /home/ubuntu/workUp/venv/bin/gunicorn -b localhost:8000 -w 4 workup:app
```

* The supervisor utility uses configuration files that tell it what programs to monitor and how to restart them when necessary. Configuration files must be stored in /etc/supervisor/conf.d. Here is a configuration file for Microblog, which I'm going to call microblog.conf:
Create and edit a file at /etc/supervisor/conf.d/workup.conf with the configuration details
```
[program:workup]
command=/home/ubuntu/workUp/venv/bin/gunicorn -b localhost:8000 -w 4 workup:app
directory=/home/ubuntu/workUp
user=ubuntu
autostart=true
autorestart=true
stopasgroup=true
killasgroup=true
```

```sh
$ sudo supervisorctl reload
```

* Get the status of the app via `sudo supervisorctl status workup`

* Setup nginx. The workup application server powered by gunicorn is now running privately port 8000.
We now need to expose ports 80 and 443.

* Create a self-signed ssl cert
```sh
$ mkdir certs
$ openssl req -new -newkey rsa:4096 -days 365 -nodes -x509 \
  -keyout certs/key.pem -out certs/cert.pem
 ```

* Nginx installs a test site in this location that I don't really need, so I'm going to start by removing it:

```sh
$ sudo rm /etc/nginx/sites-enabled/default
```

* Add the following config in `/etc/nginx/sites-enabled/workup/:
```
server {
    # listen on port 80 (http)
    listen 80;
    server_name _;
    location / {
        # redirect any requests to the same URL but on https
        return 301 https://$host$request_uri;
    }
}
server {
    # listen on port 443 (https)
    listen 443 ssl;
    server_name _;

    # location of the self-signed SSL certificate
    ssl_certificate /home/ubuntu/workUp/certs/cert.pem;
    ssl_certificate_key /home/ubuntu/workUp/certs/key.pem;

    # write access and error logs to /var/log
    access_log /var/log/workup_access.log;
    error_log /var/log/workup_error.log;

    location / {
        # forward application requests to the gunicorn server
        proxy_pass http://localhost:8000;
        proxy_redirect off;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    location /static {
        # handle static files directly, without forwarding to the application
        alias /home/ubuntu/workUp/app/static;
        expires 30d;
    }
}
```

* Reload the config with ```sudo service nginx reload``` to enable it.

* SSL certification can be obtained for free using the [Certbot ACME client](https://certbot.eff.org)


## Usage screenshots
* The student home page allows for quick access to vital information.

![View assignments](https://raw.githubusercontent.com/Siequnu/workUp/master/assets/student_home.png)

* Teachers can create assignments targeted at one or more classes. All the uploads for this assignment will be distributed randomly among colleagues for peer-review.

![Create assignment](https://raw.githubusercontent.com/Siequnu/workUp/master/assets/create_assignment.png)

* Students can quickly check their assignments. Peer reviews can only be uploaded once the student has completed their own assignment.

![View assignments](https://raw.githubusercontent.com/Siequnu/workUp/master/assets/view_assignments.png)

* Students can check how many of their colleagues have downloaded their work and submitted peer reviews.

![File Stats](https://raw.githubusercontent.com/Siequnu/workUp/master/assets/file_stats.png)

* Teachers can create forms to guide the students through a peer review process. As the students get more comfortable with the peer review process, the teacher can edit the form
to allow the students more freedom with the structure of their peer review.

![Submit peer review](https://raw.githubusercontent.com/Siequnu/workUp/master/assets/submit_peerreview.png)


