#!/bin/bash

sudo su
cd /home/daniel_tesfai/pay-telebirr/
git pull
source venv/bin/activate
cd src
python manage.py makemigrations gift
python manage.py makemigrations telebirr
python manage.py makemigrations paypal
python manage.py migrate --run-syncdb
uwsgi --ini pay_telebirr_uwsgi.ini


https://storage.googleapis.com/kin-project-352614-kinmusic-storage/Media_Files/Tracks_Cover_Images/Ansimalee_kalbekalcoverimage.jpeg