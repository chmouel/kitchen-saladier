#!/bin/bash
TOX_TARGET=integration
# TODO(chmou): get that from .gitreview file instead
GERRIT_BASE_URL=http://gerrit.sf.ring.enovance.com

export SALADIER_INTEG_CONF=/tmp/saladier-${TOX_TARGET}.conf

export SERVICE_ENDPOINT="http://${KEYSTONE_PORT_35357_TCP_ADDR}:35357/v2.0"
export SERVICE_TOKEN=${KEYSTONE_ENV_KEYSTONE_ADMIN_TOKEN}

function check_up() {
    service=$1
    host=$2
    port=$3

    max=30
    # check that the saladier is up

    counter=1
    while true;do
        python -c "import socket;s = socket.socket(socket.AF_INET, socket.SOCK_STREAM);s.connect(('$host', $port))" >/dev/null 2>/dev/null && break || echo "Waiting that $service on ${host}:${port} is started (sleeping for 5)"

        if [[ ${counter} == ${max} ]];then
            echo "Could not connect to saladier after some time"
            echo "Investigate locally the logs with fig logs"
            exit 1
        fi

        sleep 5

        (( counter++ ))
    done

}
function reprovision_virtualenv() {
    source /virtualenv/bin/activate
    pip install -e. -rrequirements.txt -rtest-requirements.txt
}

function update_keystone_endpoint() {
    keystone service-list |grep ci | awk '{print $2}'|xargs -r keystone service-delete
    keystone endpoint-list|grep 8777| awk '{print $2}'|xargs -r keystone endpoint-delete

    /usr/bin/keystone service-create --name=saladier --type=ci --description="CI validation Service"
    export SALADIER_ENDPOINT_USER="http://${SALADIER_PORT_8777_TCP_ADDR}:8777"

    /usr/bin/keystone endpoint-create \
                      --region RegionOne \
                      --service-id=`keystone service-list | grep saladier | tr -s ' ' | cut -d \  -f 2` \
                      --publicurl=${SALADIER_ENDPOINT_USER} \
                      --internalurl=${SALADIER_ENDPOINT_USER} \
                      --adminurl=${SALADIER_ENDPOINT_USER}
}

function recreate_configure_database() {
    cat <<EOF>/tmp/saladier.conf
[DEFAULT]
debug=True

[api]
api_paste_config=/code/etc/saladier/api_paste.ini

[keystone_authtoken]
signing_dir = /tmp/saladier-signing-dir
admin_tenant_name = service
admin_password = ${SALADIER_USER_PASSWORD}
admin_user = saladier_admin
identity_uri = http://${KEYSTONE_PORT_35357_TCP_ADDR}:35357

[database]
connection=mysql+pymysql://saladier:${KEYSTONE_1_ENV_KEYSTONE_DB_PASSWORD}@${DB_PORT_3306_TCP_ADDR}/saladier
EOF

    # TODO(chmouel): make that unittest and functional not using the same DB
    mysql -h ${DB_PORT_3306_TCP_ADDR} -u root -p${DB_ENV_DB_ROOT_PASSWORD} mysql <<EOF
DROP DATABASE IF EXISTS saladier;
CREATE DATABASE saladier;
GRANT ALL PRIVILEGES ON saladier.* TO
    'saladier'@'%' IDENTIFIED BY '${KEYSTONE_1_ENV_KEYSTONE_DB_PASSWORD}'
EOF

    # Create schema and upgrade
    saladier-dbsync --config-file /tmp/saladier.conf create_schema
    saladier-dbsync --config-file /tmp/saladier.conf upgrade
}

function configure_functional_tests() {
    cat <<EOF>${SALADIER_INTEG_CONF}
[DEFAULT]
admin_name = saladier_admin
admin_password = ${SALADIER_USER_PASSWORD}
admin_tenant_name = service
auth_url = http://${KEYSTONE_PORT_35357_TCP_ADDR}:35357/v2.0
user_tenant_name = saladier
user_name = saladier_user1
user_password = ${SALADIER_USER_PASSWORD}
EOF
}

# Update saladierclient to master unless we have the tag Saladierclient-Review
# see developer doc for more information about how it work.
function saladierclient_git_update() {
    local review_number=$(git log -n1|sed -n '/SaladierClient-Review/ {s/.*: \([0-9]*\)/\1/;p ;}')

    # It would only work on second run when the tox is already populated, sorry!
    if [[ ! -d .tox/${TOX_TARGET}/src/saladierclient ]];then
        return
    fi

    pushd .tox/${TOX_TARGET}/src/saladierclient >/dev/null
    git reset --hard
    git clean -ffdx -e .tox

    if [[ ${review_number} ]];then
        REF_ID=$(curl -s -L \
                      "${GERRIT_BASE_URL}/changes/?q=${review_number}&o=CURRENT_REVISION&o=CURRENT_COMMIT" |
                        sed '1d' | # NOTE(chmou): gerrit rest come back with some garbage as first line
                        python -c "import sys, json; a=json.load(sys.stdin);print a[0]['revisions'].items()[0][1]['fetch'].items()[0][1]['ref']")
        git fetch --all
        git fetch ${GERRIT_BASE_URL}/r/python-saladierclient ${REF_ID}
        git checkout -B review/${review_number} FETCH_HEAD
    else
        git checkout master
        git pull
    fi

    popd >/dev/null
}
set -fex

check_up saladier ${SALADIER_PORT_8777_TCP_ADDR} 8777
check_up keystone ${KEYSTONE_PORT_35357_TCP_ADDR} 35357

reprovision_virtualenv
saladierclient_git_update
update_keystone_endpoint
recreate_configure_database

configure_functional_tests
tox -e ${TOX_TARGET}
