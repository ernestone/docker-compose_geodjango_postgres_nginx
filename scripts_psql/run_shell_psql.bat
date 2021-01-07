@echo off
REM Copyright (c) 2012-2019, EnterpriseDB Corporation.  All rights reserved

REM PostgreSQL server psql runner script for Windows

SET server=192.168.0.54
SET database=postgres
SET port=5432
SET username=postgres

SET PGCLIENTENCODING=WIN1252
chcp 1252

REM Run psql
"C:\Postgres\bin\psql.exe" -h %server% -U %username% -d %database% -p %port%

pause


