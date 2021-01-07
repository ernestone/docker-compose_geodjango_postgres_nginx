FROM python:3.8-slim
ENV PYTHONUNBUFFERED 1
ENV LANG C.UTF-8

ARG DJANGO_ENV

ENV DJANGO_ENV=${DJANGO_ENV}

RUN mkdir /opt/project
WORKDIR /opt/project
COPY . .

RUN set -e

RUN apt-get update -qq
RUN apt-get install -y -qq binutils postgresql-client libproj-dev gdal-bin
RUN apt install -y netcat
RUN pip install --no-cache-dir pipenv && \
    pipenv install $(test "${DJANGO_ENV}" = prod || echo "--dev --skip-lock") --deploy --system --clear
RUN if [ "${DJANGO_ENV}" = "prod" ]; then pip uninstall pipenv -y; fi

RUN chmod +x ./scripts_django/*
ENV PATH="/opt/project/scripts_django:${PATH}"

RUN mkdir -p /vol/data/logs
RUN mkdir -p /vol/data/load_dir

ENV PYTHON_LOGS_DIR=/vol/data/logs
ENV DATA_DIR_SAMPLE=/vol/data/load_dir

RUN mkdir -p /vol/web/media
RUN mkdir -p /vol/web/static

#RUN adduser --disabled-password --gecos '' user
#RUN chown -R user:user /vol/web
#RUN chown -R rwx /vol/web
#USER user

CMD ["entrypoint_django.sh"]