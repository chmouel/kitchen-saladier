#!/bin/bash
# NOTE(chmouel): This come from kolla dockerfiles but finally fixed it to wait
# mariadbmaster and move service registration to down service (saladier)
set -xve

: ${KEYSTONE_ADMIN_PASSWORD:=password}
: ${ADMIN_TENANT_NAME:=admin}

# TODO(chmou): put a counter
while true;do
    if mysqladmin -h ${MARIADBMASTER_PORT_3306_TCP_ADDR} -u root -p${DB_ROOT_PASSWORD} status > /dev/null;then
        break
    else
        sleep 5
    fi
done


if ! [ "$KEYSTONE_ADMIN_TOKEN" ]; then
    KEYSTONE_ADMIN_TOKEN=$(openssl rand -hex 15)
fi

if ! [ "$KEYSTONE_DB_PASSWORD" ]; then
    KEYSTONE_DB_PASSWORD=$(openssl rand -hex 15)
fi

mysql -h ${MARIADBMASTER_PORT_3306_TCP_ADDR} -u root -p${DB_ROOT_PASSWORD} mysql <<EOF
DROP DATABASE IF EXISTS keystone;
CREATE DATABASE keystone;
GRANT ALL PRIVILEGES ON keystone.* TO
    'keystone'@'%' IDENTIFIED BY '${KEYSTONE_DB_PASSWORD}'
EOF

crudini --set /etc/keystone/keystone.conf \
    database \
    connection \
    "mysql://keystone:${KEYSTONE_DB_PASSWORD}@${MARIADBMASTER_PORT_3306_TCP_ADDR}:${MARIADBMASTER_PORT_3306_TCP_PORT}/keystone"

crudini --set /etc/keystone/keystone.conf \
    DEFAULT \
    admin_token \
    "${KEYSTONE_ADMIN_TOKEN}"

crudini --del /etc/keystone/keystone.conf \
        DEFAULT \
        log_file
crudini --del /etc/keystone/keystone.conf \
        DEFAULT \
        log_dir
crudini --set /etc/keystone/keystone.conf DEFAULT use_stderr True

cat /etc/keystone/keystone.conf

/usr/bin/keystone-manage db_sync

/usr/bin/keystone-manage pki_setup --keystone-user keystone --keystone-group keystone

/usr/bin/keystone-all &
PID=$!

# TODO(sdake) better would be to retry each keystone operation
/usr/bin/sleep 5

export SERVICE_TOKEN="${KEYSTONE_ADMIN_TOKEN}"
export SERVICE_ENDPOINT="http://127.0.0.1:35357/v2.0"

# Create the admin user
keystone user-get admin 2>/dev/null || \
    /usr/bin/keystone user-create --name admin --pass ${KEYSTONE_ADMIN_PASSWORD}
keystone role-get admin 2>/dev/null || \
    /usr/bin/keystone role-create --name admin
keystone tenant-get ${ADMIN_TENANT_NAME} 2>/dev/null || \
    /usr/bin/keystone tenant-create --name ${ADMIN_TENANT_NAME}
keystone user-role-list --user admin --tenant ${ADMIN_TENANT_NAME} || \
    /usr/bin/keystone user-role-add --user admin --role admin --tenant ${ADMIN_TENANT_NAME}

/usr/bin/sleep 5

kill -TERM $PID

# TODO(sdake) better here would be to check ps for the existance of $PID
/usr/bin/sleep 2

echo "Running keystone service."
exec /usr/bin/keystone-all
