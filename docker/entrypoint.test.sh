#!/bin/sh
uv sync --frozen --no-dev --group test
uv run manage.py collectstatic --no-input
uv run manage.py test -v 3
