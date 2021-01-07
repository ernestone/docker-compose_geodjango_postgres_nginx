# Install a package with pipenv to refresh Pipfile
docker-compose run sample_app pipenv install palettable

# Para recrear service django despues de update
docker-compose build sample_app

# Para borrar el volume con la bbdd postgis
docker volume ls # Para ver nombre interno volumen (path_dir_+_db_postgis_vol)
docker volume rm nombre_vol

# Makemigrations iniciales para bbdd nueva
docker-compose run sample_app bash -c "./scripts_docker/wait_until_startup_postgres.sh && python manage.py makemigrations"
