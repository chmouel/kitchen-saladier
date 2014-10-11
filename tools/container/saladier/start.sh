#!/bin/bash
set -xe

pip install -e .

export SERVICE_ENDPOINT="http://${KEYSTONE_PORT_35357_TCP_ADDR}:35357/v2.0"
export SERVICE_TOKEN=${KEYSTONE_ENV_KEYSTONE_ADMIN_TOKEN}

# We need to wait that it's up and that it was running
while true; do 
    if keystone service-list 2>/dev/null >/dev/null;then
        break
    else
        sleep 5
    fi
done

# Create the keystone service and endpoint cause we could not before in keystone image (silly I know)
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

# We need to wait that it has restarted after keystone was bootstraping
while true; do 
    if /usr/bin/keystone user-role-add --user saladier --role admin --tenant service;then
        break
    else
        sleep 5
    fi
done

cat <<EOF>/tmp/saladier.conf
[DEFAULT]
api_paste_config=/code/etc/saladier/api_paste.ini
debug=True

[keystone_authtoken]
signing_dir = /tmp/saladier-signing-dir
admin_tenant_name = service
admin_password = ${SALADIER_USER_PASSWORD}
admin_user = saladier
identity_uri = http://${KEYSTONE_PORT_35357_TCP_ADDR}:35357
EOF

exec saladier-api --config-file /tmp/saladier.conf
