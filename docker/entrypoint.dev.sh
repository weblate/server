#!/bin/sh
poetry install --no-root
if [ "$CELERY_WORKER" = "true" ]
then
    if [ -z "$CELERY_QUEUES" ]
    then
        celery -A neatplus worker -l info
    else
        celery -A neatplus worker -l info -Q "$CELERY_QUEUES"
    fi
else
    poetry run python ./manage.py collectstatic --no-input
    poetry run python ./manage.py migrate --no-input
    poetry run python ./manage.py import_default_email_template
    poetry run python ./manage.py runserver_plus 0.0.0.0:8000 || ./manage.py runserver 0.0.0.0:8000
fi
