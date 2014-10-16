#!/bin/bash
set -ex

while true;do
    if mysqladmin -h ${DB_PORT_3306_TCP_ADDR} -u root -p${DB_ROOT_PASSWORD} status > /dev/null;then
        break
    else
        sleep 5
    fi
done

mysql -h ${DB_PORT_3306_TCP_ADDR} -u root -p${DB_ROOT_PASSWORD} mysql <<EOF
CREATE DATABASE IF NOT EXISTS saladier;
GRANT ALL PRIVILEGES ON saladier.* TO
    'saladier'@'%' IDENTIFIED BY '${SALADIER_DB_PASSWORD}'
EOF

source /virtualenv/bin/activate
pip install -e.

cat <<EOF>/tmp/saladier.conf
[database]
connection=mysql+pymysql://saladier:${SALADIER_DB_PASSWORD}@${DB_PORT_3306_TCP_ADDR}/saladier
EOF
saladier-dbsync --config-file /tmp/saladier.conf

# We probably want to make it a bit better next (i.e: py34)
python setup.py testr --slowest

