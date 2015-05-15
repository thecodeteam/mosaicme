#!/bin/sh

# Collect static files
python /app/mosaicme-web/manage.py collectstatic --noinput

service nginx start

if [ ! ps ax |grep -v grep |grep nginx > /dev/null ];
then
        echo "nginx is not running"
        exit 2
fi

gunicorn --name=mosaicme --bind=0.0.0.0:9000 --workers 3 web.wsgi:application
