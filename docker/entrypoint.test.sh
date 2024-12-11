#!/bin/sh
poetry install --no-root
poetry run python ./manage.py collectstatic --no-input
poetry run python ./manage.py test -v 3
