#!/bin/bash

set -e

apt-get update -qq
apt-get install -y -qq binutils postgresql-client libproj-dev gdal-bin
apt install build-essential zlib1g-dev libncurses5-dev libgdbm-dev libnss3-dev libssl-dev libsqlite3-dev libreadline-dev libffi-dev curl libbz2-dev wget
wget https://www.python.org/ftp/python/3.8.6/Python-3.8.6.tgz
tar xzf Python-3.8.6.tgz
cd Python-3.8.6
./configure --enable-optimizations
make altinstall

pip install --no-cache-dir pipenv

pipenv install $(test "${DJANGO_ENV}" = prod || echo "--dev --skip-lock") --deploy --clear
