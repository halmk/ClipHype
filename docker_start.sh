#!/bin/bash
service mysql start
#echo 'CREATE DATABASE cliphype;' | mysql -u root
cd cliphype/
export DJANGO_SETTINGS_MODULE=cliphype.local_settings
nohup redis-server > ~/redis.log &
nohup celery -A cliphype worker --loglevel=INFO --concurrency=1 > ~/celery.log &
python3 manage.py makemigrations
python3 manage.py migrate
#/bin/bash
