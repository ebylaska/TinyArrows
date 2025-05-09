#!/bin/bash

if [ ! -f /docker-entrypoint-initdb.d/backup/eric3.sql ]; then
    gunzip /docker-entrypoint-initdb.d/backup/eric3.sql.gz
fi

DB_EXISTS=$(mariadb -uarrows -preaction -e "SHOW DATABASES LIKE 'TNT_Project';" | grep "TNT_Project" > /dev/null; echo "$?")

if [ "$DB_EXISTS" -eq 1 ]; then
    mariadb -uarrows -preaction TNT_Project < /docker-entrypoint-initdb.d/backup/eric3.sql
fi

