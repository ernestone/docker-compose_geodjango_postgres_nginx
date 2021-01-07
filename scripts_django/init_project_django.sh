# Iniciar modelo django habiendo indicado en settings.py la conexión de la BBDD (param 'zero' para inicializar)
docker-compose run sample_app bash -c "./scripts_docker/wait_until_startup_postgres.sh && python manage.py migrate"

# Crear superusuario (test sample@mail.com sample_123zxc)
docker-compose run sample_app python manage.py createsuperuser

# Carga fixture
docker-compose run sample_app python manage.py loaddata

# Carga datos sample
docker-compose run sample_app python manage.py load_data_dir
