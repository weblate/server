#!/bin/sh
if [ "$CELERY_WORKER" = "true" ]
then
    if [ -z "$CELERY_QUEUES" ]
    then
        celery -A neatplus worker -l info
    else
        celery -A neatplus worker -l info -Q "$CELERY_QUEUES"
    fi
else
    ./manage.py migrate --no-input
    ./manage.py import_default_email_template
    gunicorn neatplus.asgi:application -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000
fi
