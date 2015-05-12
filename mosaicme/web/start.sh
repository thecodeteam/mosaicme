#!/bin/sh

if [ ! -f /app/config/.env ]; then
        echo ".env file not found!"
        exit 1
fi

# Collect static files
RUN python /app/mosaicme-web/manage.py collectstatic --noinput

service nginx start

python /app/mosaicme-web/manage.py collectstatic --noinput

if [ ! ps ax | grep -v grep | grep nginx > /dev/null ];
then
        echo "nginx is not running"
        exit 2
fi

supervisord -n
