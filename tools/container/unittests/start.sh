#!/bin/bash
set -ex

while true;do
    if mysqladmin -h ${DB_PORT_3306_TCP_ADDR} -u root -p${DB_ROOT_PASSWORD} status > /dev/null;then
        break
    else
        sleep 5
    fi
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

# TODO(chmouel): make that unittest and functional not using the same DB
mysql -h ${DB_PORT_3306_TCP_ADDR} -u root -p${DB_ROOT_PASSWORD} mysql <<EOF
DROP DATABASE IF EXISTS saladierunit;
CREATE DATABASE IF NOT EXISTS saladierunit;
GRANT ALL PRIVILEGES ON saladierunit.* TO
    'saladier'@'%' IDENTIFIED BY '${SALADIER_DB_PASSWORD}'
EOF

source /virtualenv/bin/activate
pip install -e.


echo "Running tests under SQLite"
cat <<EOF>/tmp/saladier.conf
[database]
connection=sqlite://
EOF

run_tox SQLite

echo "Running tests under MySQL"
export SALADIER_DATABASE_TEST_CONNECTION="mysql+pymysql://saladier:${SALADIER_DB_PASSWORD}@${DB_PORT_3306_TCP_ADDR}/saladierunit"

cat <<EOF>/tmp/saladier.conf
[database]
connection=${SALADIER_DATABASE_TEST_CONNECTION}
EOF

# Create schema and upgrade
saladier-dbsync --config-file /tmp/saladier.conf create_schema
saladier-dbsync --config-file /tmp/saladier.conf upgrade

run_tox MySQL runonly_pythontest_formysql
