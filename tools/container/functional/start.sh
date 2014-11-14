#!/bin/bash
set -e

[[ -n ${DEBUG} ]] && set -x

function get_token() {
    tenant=$1
    user=$2
    password=$3
    curl -s -X POST \
        http://${KEYSTONE_PORT_35357_TCP_ADDR}:35357/v2.0/tokens -H "Content-Type: application/json" -d \
        "{\"auth\": {\"tenantName\": \"${tenant}\", \"passwordCredentials\": {\"username\": \"${user}\", \"password\": \"${password}\"}}}" | python -c 'import sys, json; print json.load(sys.stdin)["access"]["token"]["id"]'
}


function check_up() {
    service=$1
    host=$2
    port=$3

    max=13 # 1 minute
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

check_up saladier ${SALADIER_PORT_8777_TCP_ADDR} 8777
check_up keystone ${KEYSTONE_PORT_35357_TCP_ADDR} 35357

function exit_it {
    [[ $? != 0 ]] && echo "has failed :("
}

trap exit_it EXIT


echo "Starting functional testing"
echo "---------------------------"

echo -n "Getting admin token from Keystone: "
ADMIN_TOKEN=$(get_token service saladier_admin ${SALADIER_USER_PASSWORD})
echo "OK."


echo -n "Getting user token from Keystone: "
USER_TOKEN=$(get_token saladier saladier_user1 ${SALADIER_USER_PASSWORD})
echo "OK."


# This is our only unittest for now we will expand with a proper unittest
# framework in the future when REST class will be written. (The -f to curl would
# exit 1 if we have a 4xx or 5xx errors)

# Create a product
echo -n "Creating a product as admin: "
curl -f -s -L -H "x-auth-token: $ADMIN_TOKEN" -X POST -d 'name=yayalebogosse' -d 'team=boa' -d 'contact=thecedric@isthegreatest.com' \
     http://${SALADIER_PORT_8777_TCP_ADDR}:8777/v1/products/
echo "OK."

echo -n "Get created product as user: "
curl -f -s -L -H "x-auth-token: $USER_TOKEN" http://${SALADIER_PORT_8777_TCP_ADDR}:8777/v1/products/ | grep -q "thecedric@isthegreatest.com"
echo "OK."

echo -n "Delete created product as admin: "
curl -X DELETE -f -s -L -H "x-auth-token: $ADMIN_TOKEN" http://${SALADIER_PORT_8777_TCP_ADDR}:8777/v1/products/yayalebogosse
echo "OK."


#TODO(chmouel): Delete product

# Create a platform
echo -n "Creating a platform as admin: "
curl -f -s -L -H "x-auth-token: $ADMIN_TOKEN" -X POST -d 'name=chmoulebogosse' -d 'location=ParisEstMagique' -d 'contact=thecedric@isthegreatest.com' \
     -d 'tenant=etmontenantcestdupoulet' http://${SALADIER_PORT_8777_TCP_ADDR}:8777/v1/platforms/
echo "OK."

echo -n "Get created platform as user: "
curl -f -s -L -H "x-auth-token: $USER_TOKEN" http://${SALADIER_PORT_8777_TCP_ADDR}:8777/v1/platforms/ | grep -q "thecedric@isthegreatest.com"
echo "OK."

echo -n "Delete created platform as admin: "
curl -X DELETE -f -s -L -H "x-auth-token: $ADMIN_TOKEN" http://${SALADIER_PORT_8777_TCP_ADDR}:8777/v1/platforms/chmoulebogosse
echo "OK."

echo "Done and successfull :)"
