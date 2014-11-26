#!/bin/bash
set -xe

pip install -e .

export SERVICE_ENDPOINT="http://${KEYSTONE_PORT_35357_TCP_ADDR}:35357/v2.0"
export SERVICE_TOKEN=${KEYSTONE_ENV_KEYSTONE_ADMIN_TOKEN}

function check_keystone_up  {
    max=20 # 1 minute
    counter=1
    while true; do
        if [[ ${counter} == ${max} ]];then
            echo "Could not connect to keystone after some time"
            echo "Investigate locally the logs with fig logs"
            exit 1
        fi

        if keystone role-list | grep -q admin 2>/dev/null >/dev/null;then
            break
        fi

        sleep 5
        (( counter ++ ))
    done
}
check_keystone_up

# NOTE(chmou): go figure :( I can't catch properly with a loop so let's just wait a litle bit more
sleep 10

# Create the keystone service and endpoint cause we could not before in keystone image (silly I know)
# Make sure we don't do that every time (double silly)
if ! keystone service-list|grep -q keystone; then
    /usr/bin/keystone service-create --name=keystone --type=identity --description="Identity Service"
    export SERVICE_ENDPOINT_USER="http://${KEYSTONE_PORT_5000_TCP_ADDR}:5000/v2.0"
    export SERVICE_ENDPOINT_ADMIN="http://${KEYSTONE_PORT_35357_TCP_ADDR}:35357/v2.0"

    /usr/bin/keystone endpoint-create \
                      --region RegionOne \
                      --service-id=`keystone service-list | grep keystone | tr -s ' ' | cut -d \  -f 2` \
                      --publicurl=${SERVICE_ENDPOINT_USER} \
                      --internalurl=${SERVICE_ENDPOINT_USER} \
                      --adminurl=${SERVICE_ENDPOINT_ADMIN}

    /usr/bin/keystone service-create --name=saladier --type=ci --description="CI validation Service"
    # NOTE(chmou): we have to detect our own ip this sucks but fig don't expose it :(
    SALADIER_PORT_8777_TCP_ADDR=$(ip addr show eth0|sed -n '/inet / { s/.*inet //;s/\/.*//;p }')
    export SALADIER_ENDPOINT_USER="http://${SALADIER_PORT_8777_TCP_ADDR}:8777/v1"

    /usr/bin/keystone endpoint-create \
                      --region RegionOne \
                      --service-id=`keystone service-list | grep saladier | tr -s ' ' | cut -d \  -f 2` \
                      --publicurl=${SALADIER_ENDPOINT_USER} \
                      --internalurl=${SALADIER_ENDPOINT_USER} \
                      --adminurl=${SALADIER_ENDPOINT_USER}

    # Create an admin that we will use for admin stuff and for validating token
    /usr/bin/keystone tenant-create --name service
    /usr/bin/keystone user-create --name saladier_admin --pass ${SALADIER_USER_PASSWORD}
    /usr/bin/keystone user-role-add --user saladier_admin --role admin --tenant service

    # Create a normal user for validating Jenkins CI without admin role
    /usr/bin/keystone role-create --name Member
    /usr/bin/keystone tenant-create --name saladier
    /usr/bin/keystone user-create --name saladier_user1 --pass ${SALADIER_USER_PASSWORD}
    /usr/bin/keystone user-role-add --user saladier_user1 --role Member --tenant saladier
fi


# TODO(chmou): commonize with the other container start scripts since we are
# doubloning up here
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

# Exec Saladier
exec saladier-api --config-file /tmp/saladier.conf --debug
