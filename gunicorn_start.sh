#!/bin/bash

NAME="fdfantasy"                              #Name of the application (*)
DJANGODIR=/home/ec2-user/fdfantasy             # Django project directory (*)
SOCKFILE=/socket/gunicorn.sock        # we will communicate using this unix socket (*)
NUM_WORKERS=1                                     # how many worker processes should Gunicorn spawn (*)
DJANGO_SETTINGS_MODULE=fdfantasy.settings             # which settings file should Django use (*)
DJANGO_WSGI_MODULE=fdfantasy.wsgi                     # WSGI module name (*)

echo "Starting $NAME as `whoami`"

# Activate the virtual environment
cd $DJANGODIR
source /home/ec2-user/venv/bin/activate
export DJANGO_SETTINGS_MODULE=$DJANGO_SETTINGS_MODULE
export PYTHONPATH=$DJANGODIR:$PYTHONPATH

# Create the run directory if it doesn't exist
RUNDIR=$(dirname $SOCKFILE)
test -d $RUNDIR || mkdir -p $RUNDIR

# Start your Django Unicorn
# Programs meant to be run under supervisor should not daemonize themselves (do not use --daemon)
exec gunicorn ${DJANGO_WSGI_MODULE}:application \
  --name $NAME \
  --workers $NUM_WORKERS \
  --bind=unix:$SOCKFILE
