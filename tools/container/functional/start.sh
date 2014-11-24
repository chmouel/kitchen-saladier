#!/bin/bash
set -e
CURL_FLAG="-s"

[[ -n ${DEBUG} ]] && set -x
[[ -n ${DEBUG} ]] && CURL_FLAG="-i"

function get_token() {
    tenant=$1
    user=$2
    password=$3
    curl -s -X POST \
        http://${KEYSTONE_PORT_35357_TCP_ADDR}:35357/v2.0/tokens -H "Content-Type: application/json" -d \
        "{\"auth\": {\"tenantName\": \"${tenant}\", \"passwordCredentials\": {\"username\": \"${user}\", \"password\": \"${password}\"}}}" | python -c 'import sys, json; d=json.load(sys.stdin);print d["access"]["token"]["tenant"]["id"]+" "+d["access"]["token"]["id"]'
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
_token=$(get_token service saladier_admin ${SALADIER_USER_PASSWORD})
ADMIN_TOKEN=${_token##* }
ADMIN_TENANT_ID=${_token% *}
echo "OK."

echo -n "Getting user token from Keystone: "
USER_NAME=saladier_user1
USER_TENANT=saladier
_token=$(get_token ${USER_TENANT} ${USER_NAME} ${SALADIER_USER_PASSWORD})
USER_TOKEN=${_token##* }
USER_TENANT_ID=${_token% *}
echo "OK."


# NOTE(chmou): This is our blackbox functest suite with curl for now we will
# expand with a proper framework (i.e: tempest-lib) in the future when REST
# class will be written. (The -f to curl would exit 1 if we have a 4xx or 5xx
# errors)

echo -n "Test public version access: "
curl -f ${CURL_FLAG} -L http://${SALADIER_PORT_8777_TCP_ADDR}:8777/ |grep -q 'Paris'
echo "OK."

# Create a product
echo -n "Creating a product as admin: "
curl -f ${CURL_FLAG} -L -H "x-auth-token: $ADMIN_TOKEN" -X POST -d 'name=yayalebogosse' -d 'team=boa' -d 'contact=thecedric@isthegreatest.com' \
     http://${SALADIER_PORT_8777_TCP_ADDR}:8777/v1/products
echo "OK."

echo -n "Associate a product to a version: "
curl -f ${CURL_FLAG} -L -H "x-auth-token: $ADMIN_TOKEN" -X POST -d 'product=yayalebogosse' -d 'url=http://anywhereyoulike' \
     -d 'version=1.0' \
     http://${SALADIER_PORT_8777_TCP_ADDR}:8777/v1/versions
echo "OK."

echo -n "Subscribe tenant ${USER_NAME} to product: "
curl -f ${CURL_FLAG} -L -H "x-auth-token: $ADMIN_TOKEN" -X POST -d 'product_name=yayalebogosse' -d "tenant_id=${USER_TENANT_ID}" \
     -d 'version=1.0' \
     http://${SALADIER_PORT_8777_TCP_ADDR}:8777/v1/subscriptions
echo "OK".

echo -n "Listing products: "
curl -f ${CURL_FLAG} -L -H "x-auth-token: $USER_TOKEN" http://${SALADIER_PORT_8777_TCP_ADDR}:8777/v1/products/ | grep -q 'yayalebogosse'
echo "OK."

echo -n "Get product directly: "
curl -f ${CURL_FLAG} -L -H "x-auth-token: $USER_TOKEN" http://${SALADIER_PORT_8777_TCP_ADDR}:8777/v1/products/yayalebogosse \
    | grep -q "thecedric@isthegreatest.com"
echo "OK."

echo -n "Get product version directly: "
curl -f ${CURL_FLAG} -L -H "x-auth-token: $USER_TOKEN" http://${SALADIER_PORT_8777_TCP_ADDR}:8777/v1/products/yayalebogosse/1.0 | \
    grep -q "validated_on"
echo "OK."

echo -n "Delete subscription of ${USER_NAME} to our product: "
curl -f ${CURL_FLAG} -L -H "x-auth-token: $ADMIN_TOKEN" -X DELETE \
     http://${SALADIER_PORT_8777_TCP_ADDR}:8777/v1/subscriptions/yayalebogosse/${USER_TENANT_ID}
echo "OK"

echo -n "Delete Association between product and version: "
curl -f ${CURL_FLAG} -L -H "x-auth-token: $ADMIN_TOKEN" -X DELETE \
     http://${SALADIER_PORT_8777_TCP_ADDR}:8777/v1/versions/yayalebogosse/1.0
echo "OK"

echo -n "Delete created product as admin: "
curl -f ${CURL_FLAG} -X DELETE -L -H "x-auth-token: $ADMIN_TOKEN" http://${SALADIER_PORT_8777_TCP_ADDR}:8777/v1/products/yayalebogosse
echo "OK."

# Create a platform
echo -n "Creating a platform as admin: "
curl -f ${CURL_FLAG} -L -H "x-auth-token: $ADMIN_TOKEN" -X POST -d 'name=chmoulebogosse' -d 'location=ParisEstMagique' \
     -d 'contact=thecedric@isthegreatest.com' \
     -d 'tenant_id=0000101010101' http://${SALADIER_PORT_8777_TCP_ADDR}:8777/v1/platforms
echo "OK."

echo -n "Get created platform as user: "
curl -f ${CURL_FLAG} -L -H "x-auth-token: $USER_TOKEN" http://${SALADIER_PORT_8777_TCP_ADDR}:8777/v1/platforms/ | grep -q "thecedric@isthegreatest.com"
echo "OK."

echo -n "Delete created platform as admin: "
curl -X DELETE -f ${CURL_FLAG} -L -H "x-auth-token: $ADMIN_TOKEN" http://${SALADIER_PORT_8777_TCP_ADDR}:8777/v1/platforms/chmoulebogosse
echo "OK."

echo "Done and successful :)"
