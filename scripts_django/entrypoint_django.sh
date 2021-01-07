#!/bin/bash

# Para que se pare en el primer error que encuentre
set -e

"$(dirname "$0")/../scripts_docker/wait_until_startup_postgres.sh"

if [ "$DJANGO_ENV" = "dev" ]
then
    python manage.py migrate --noinput
    python manage.py runserver 0.0.0.0:8000
else
    python manage.py collectstatic --noinput
    gunicorn --bind 0.0.0.0:8000 --timeout $GUNICORN_TIMEOUT django_base.wsgi
fi