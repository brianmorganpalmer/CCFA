.. _installation:

##########
Installing
##########

Installing the automated pipeline backend
=========================================

Just a one liner::

   pip install -e 'git+https://bitbucket.org/biobakery/ccfa.git@master#egg=mibc-0.0.1'


Installing the web front-end
============================

CentOS 6
________

Install and configure the necessary packages::

  sudo yum install -y \
      python-virtualenv python-ldap \
      mysql.x86_64 mysql-devel.x86_64 mysql-libs.x86_64 mysql-server.x86_64

  mysql_secure_installation


Note that the choice of database backend isn't crucial; just be sure
to properly set-up either postgres or mysql.

Create a virtual environment for the packages::

  mkdir ccfa; cd ccfa
  virtualenv env
  source env/bin/activate

Clone and install the ccfa code::

  git clone https://bitbucket.org/biobakery/ccfa.git
  cd ccfa
  python setup.py develop

Install the web dependencies::

  cd web_cms
  pip install -r requirements.txt

Setup Django's database::

  cd ..
  # be sure to run the SQL statement that the below command prints out
  python setup.py web_setup
  cd web_cms
  python manage.py syncdb
  python manage.py loaddata new.json

Edit the ``mibc`` settings file to match your environment::

  cd ../mibc
  emacs settings.py # or your editor of choice

Finally, start up a web worker to serve the application. We use
gunicorn, but one could use whatever::

  pip install gunicorn
  nohup gunicorn wsgi:application > /tmp/gunicorn.log 2>&1

We use nginx to serve static files and act as a reverse proxy, for an
example of our configuration, check out the
``web_cms/deploy/nginx.conf`` file.

