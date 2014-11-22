#!/bin/bash
set -ex

cnt=0
while true;do
    if [[ $cnt == 20 ]];then
        echo "Could not connect to mysql, investigate!"
        exit 1
    fi
    if mysqladmin -h ${DB_PORT_3306_TCP_ADDR} -u root -p${DB_ROOT_PASSWORD} status > /dev/null;then
        break
    fi
    sleep 5
    (( cnt++ ))
done


run_tox() {
    target=$1
    only_for_python_targets=$2

    # Running tox, stop as soon as we get a failure
    for i in $(tox -l); do
        # NOTE(chmou): don't run the other tox targets if we just want to
        # validate the underlying DB and then run only the python unittests not
        # the pep8 and other target tox like that
        [[ -n $only_for_python_targets && ${i} != py* ]] && continue

        # NOTE(chmou): We do that cause py27 and py34 testrepository cache is not a
        # compatible format :-(
        rm -rf .testrepository
        echo "Running $i under ${target}"
        tox -e${i}
    done
}

source /virtualenv/bin/activate
pip install -e.

### MySQL
echo "Running tests under MySQL"
mysql -h ${DB_PORT_3306_TCP_ADDR} -u root -p${DB_ROOT_PASSWORD} mysql <<EOF
DROP DATABASE IF EXISTS saladierunit;
CREATE DATABASE IF NOT EXISTS saladierunit;
GRANT ALL PRIVILEGES ON saladierunit.* TO
    'saladier'@'%' IDENTIFIED BY '${SALADIER_DB_PASSWORD}'
EOF
export SALADIER_DATABASE_TEST_CONNECTION="mysql+pymysql://saladier:${SALADIER_DB_PASSWORD}@${DB_PORT_3306_TCP_ADDR}/saladierunit"

cat <<EOF>/tmp/saladier.conf
[database]
connection=${SALADIER_DATABASE_TEST_CONNECTION}
EOF

# Create schema and upgrade
saladier-dbsync --config-file /tmp/saladier.conf create_schema
saladier-dbsync --config-file /tmp/saladier.conf upgrade

run_tox MySQL runonly_pythontest_formysql

### PostgresSQL
echo "Running tests under PostgresSQL"
export SALADIER_DATABASE_TEST_CONNECTION="postgres://postgres:${SALADIER_DB_PASSWORD}@${POSTGRES_PORT_5432_TCP_ADDR}/saladier"

PGPASSWORD=${SALADIER_DB_PASSWORD} dropdb --if-exists -U postgres -h${POSTGRES_PORT_5432_TCP_ADDR} saladier
PGPASSWORD=${SALADIER_DB_PASSWORD} createdb -U postgres -h${POSTGRES_PORT_5432_TCP_ADDR} saladier

cat <<EOF>/tmp/saladier.conf
[database]
connection=${SALADIER_DATABASE_TEST_CONNECTION}
EOF

# Create schema and upgrade
saladier-dbsync --config-file /tmp/saladier.conf create_schema
saladier-dbsync --config-file /tmp/saladier.conf upgrade

run_tox PostgresSQL runonly_pythontest_formysql

### SQLITE
# NOTE(chmou): need to be at the end after the others cause it generates the
# cover and docs.
echo "Running tests under SQLite"
export SALADIER_DATABASE_TEST_CONNECTION="sqlite://"
run_tox SQLite
