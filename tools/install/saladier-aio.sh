#!/bin/bash
set -xefu

# You definitively want to change those
export PUBLIC_IP=localhost
export PASSWORD=password

# You may want to change those
export SALADIER_ENDPOINT_USER="http://${PUBLIC_IP}:8777"
export SERVICE_ENDPOINT_USER="http://${PUBLIC_IP}:5000/v2.0"
export SERVICE_ENDPOINT="http://${PUBLIC_IP}:35357/v2.0"
export SERVICE_TOKEN=${PASSWORD}

### Here come the dragons

# Setup repository
yum install -y https://rdo.fedorapeople.org/rdo-release.rpm

cat <<EOF>/etc/yum.repos.d/saladier.repo
[saladier]
name=Saladier
baseurl=http://kitchenbot.chmouel.com/rpm
enabled=1
metadata_expire=1d
gpgcheck=0
skip_if_unavailable=True
EOF

# Install the packages
yum -y install kitchen-saladier openstack-keystone mariadb mariadb-server sudo

# Start and configure MySQL
systemctl enable mariadb
systemctl start mariadb

mysql -uroot mysql <<EOF
DROP DATABASE IF EXISTS keystone;
DROP DATABASE IF EXISTS saladier;
CREATE DATABASE keystone;
CREATE DATABASE saladier;
GRANT ALL PRIVILEGES ON keystone.* TO 'keystone'@'%' IDENTIFIED BY '${PASSWORD}';
GRANT ALL PRIVILEGES ON keystone.* TO 'keystone'@'localhost' IDENTIFIED BY '${PASSWORD}';
GRANT ALL PRIVILEGES ON saladier.* TO 'saladier'@'localhost' IDENTIFIED BY '${PASSWORD}';
EOF

# Configure keystone
sed -i -e "s,^#admin_token[ ]*=.*,admin_token=${PASSWORD}," /etc/keystone/keystone.conf
sed -i -e "s,^#connection[ ]*=.*,connection=mysql://keystone:${PASSWORD}@localhost/keystone," /etc/keystone/keystone.conf

# Configure saladier
# NOTE(chmou): We have a bug with Saladier oslo config generation which is
# tricky to fix, let's do a static file for now until we find a proper way.
#
# We should use this instead in the future :
#
# sed -i -e "s,^connection[ ]*=.*,connection=mysql://saladier:${PASSWORD}@localhost/saladier," /etc/saladier/saladier.conf
# sed -i -e "s,^#admin_password[ ]*=.*,admin_password=${PASSWORD}," /etc/saladier/saladier.conf
# sed -i -e "s,^#admin_user[ ]*=.*,admin_user=admin," /etc/saladier/saladier.conf
# sed -i -e "s,^#auth_protocol[ ]*=.*,auth_protocol=http," /etc/saladier/saladier.conf

cat <<EOF>/etc/saladier/saladier.conf
[DEFAULT]
debug=True

[api]
api_paste_config=/etc/saladier/api_paste.ini

[keystone_authtoken]
signing_dir = /tmp/saladier-signing-dir
admin_tenant_name = service
admin_password = ${PASSWORD}
admin_user = saladier_admin
identity_uri = http://localhost:35357
auth_uri = http://localhost:35357

[database]
connection=mysql://saladier:${PASSWORD}@localhost/saladier
EOF

# DB configuration for Keystone
sudo -u keystone /usr/bin/keystone-manage db_sync
/usr/bin/keystone-manage pki_setup --keystone-user keystone --keystone-group keystone

# DB configuration for Saladier
sudo -u saladier /usr/bin/saladier-dbsync --config-file /etc/saladier/saladier.conf create_schema
sudo -u saladier /usr/bin/saladier-dbsync --config-file /etc/saladier/saladier.conf upgrade

# Enable and Start Keystone
systemctl enable openstack-keystone
systemctl start openstack-keystone

sleep 2

# Enable and Start Saladier
systemctl enable kitchen-saladier
systemctl start kitchen-saladier

sleep 2

# Add Keystone endpoint
/usr/bin/keystone service-create --name=keystone --type=identity --description="Identity Service"
/usr/bin/keystone endpoint-create \
                  --region RegionOne \
                  --service-id=`keystone service-list | grep keystone | tr -s ' ' | cut -d \  -f 2` \
                  --publicurl=${SERVICE_ENDPOINT_USER} \
                  --internalurl=${SERVICE_ENDPOINT_USER} \
                  --adminurl=${SERVICE_ENDPOINT}

# Add Saladier endpoint
/usr/bin/keystone service-create --name=saladier --type=ci --description="CI validation Service"
/usr/bin/keystone endpoint-create --region RegionOne \
                  --service-id=`keystone service-list | grep saladier | tr -s ' ' | cut -d \  -f 2` \
                  --publicurl=${SALADIER_ENDPOINT_USER} \
                  --internalurl=${SALADIER_ENDPOINT_USER} \
                  --adminurl=${SALADIER_ENDPOINT_USER}

# Add Keystone Admin
/usr/bin/keystone user-create --name admin --pass ${PASSWORD}
/usr/bin/keystone role-create --name admin
/usr/bin/keystone tenant-create --name admin
/usr/bin/keystone user-role-add --user admin --role admin --tenant admin

# Saladier token validation user (needs to be an admin)
/usr/bin/keystone tenant-create --name service
/usr/bin/keystone user-create --name saladier_admin --pass ${PASSWORD}
/usr/bin/keystone user-role-add --user saladier_admin --role admin --tenant service

# Saladier first user
/usr/bin/keystone role-create --name Member
/usr/bin/keystone tenant-create --name saladier
/usr/bin/keystone user-create --name saladier_user1 --pass ${PASSWORD}
/usr/bin/keystone user-role-add --user saladier_user1 --role Member --tenant saladier

# Test it
unset SERVICE_TOKEN SERVICE_ENDPOINT

curl -o/tmp/ks http://ep.chmouel.com:8080/ks
eval $(bash /tmp/ks -s localhost service:saladier_admin password)
curl -s -H "x-auth-token: $TOKEN" -X GET http://localhost:8777/v1/products/ | python -mjson.tool
