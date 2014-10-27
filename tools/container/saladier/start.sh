#!/bin/bash
set -xe

pip install -e .

export SERVICE_ENDPOINT="http://${KEYSTONE_PORT_35357_TCP_ADDR}:35357/v2.0"
export SERVICE_TOKEN=${KEYSTONE_ENV_KEYSTONE_ADMIN_TOKEN}

# We need to wait that it's up and that it was running
while true; do 
    if keystone role-list | grep -q admin 2>/dev/null >/dev/null;then
        break
    else
        sleep 5
    fi
done

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
                      --adminurl=http:${SERVICE_ENDPOINT_ADMIN}

    /usr/bin/keystone user-create --name saladier --pass ${SALADIER_USER_PASSWORD}
    /usr/bin/keystone tenant-create --name service
    /usr/bin/keystone user-role-add --user saladier --role admin --tenant service
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
admin_user = saladier
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
