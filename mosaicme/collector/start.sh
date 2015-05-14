#!/bin/sh

if [ ! -f /app/config/.env ]; then
        echo ".env file not found!"
        exit 1
fi

supervisord -n
