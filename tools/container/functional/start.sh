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

function curl_it {
    local msg=$1
    local url=$2
    local token=$3
    local method=$4
    local datas=$5
    local grep=$6
    local _curl_datas=""
    [[ ${datas} == " " ]] && datas= # NOTE(chmou): placeholders when we don't want to go on with the arg
    [[ ${url} != http://* ]] && url=http://${SALADIER_PORT_8777_TCP_ADDR}:8777/v1${url}

    for x in ${datas//|/ };do
        _curl_datas="${_curl_datas} -d $x"
    done

    echo -n "$msg: "
    curl -f -i -o /tmp/output.json ${CURL_FLAG} ${_curl_datas} -L -X ${method} -H "x-auth-token: ${token}" ${url} || failed=$?

    if [[ -n ${failed} || -n ${grep} ]];then
        grep -q ${grep} /tmp/output.json || failed=$?
    fi

    if [[ -n ${failed} ]];then
        echo  "Failed."
        if [[ -n ${grep} ]];then
            echo "------- Error while trying to grep '${grep}' in the json output -------"
        else
            echo "------- ERROR -------"
        fi
        cat /tmp/output.json
        echo "------- ERROR -------"
        exit 1
    else
        echo "OK."
    fi
}

# Create a product
curl_it "Creating a product as admin" \
         /products \
         ${ADMIN_TOKEN} \
         POST \
         "team=boa|name=yayalebogosse|contact=cedric@isthegreatest.com"

curl_it "Associate a product to a version" \
        /versions \
        ${ADMIN_TOKEN} \
        POST \
        'product=yayalebogosse|url=http://anywhereyoulike|version=1.0'

curl_it "Subscribe tenant ${USER_NAME} to product" \
        /subscriptions \
        ${ADMIN_TOKEN} \
        POST \
        "product_name=yayalebogosse|tenant_id=${USER_TENANT_ID}"

curl_it "Listing products" \
        /products/ \
        ${USER_TOKEN} \
        GET \
        " " \
        "yayalebogosse"

curl_it "Get product directly" \
        /products/yayalebogosse \
        ${USER_TOKEN} \
        GET \
        " " \
        "cedric@isthegreatest.com"

curl_it "Get product version directly" \
        /products/yayalebogosse/1.0 \
        ${USER_TOKEN} \
        GET \
        " " \
        "validated_on"

curl_it "Delete subscription of ${USER_NAME} to our product" \
        /subscriptions/yayalebogosse/${USER_TENANT_ID} \
        ${ADMIN_TOKEN} \
        DELETE

curl_it "Delete Association between product and version" \
        /versions/yayalebogosse/1.0 \
        ${ADMIN_TOKEN} \
        DELETE

curl_it "Delete created product as admin" \
        /products/yayalebogosse \
        ${ADMIN_TOKEN} \
        DELETE

curl_it "Creating a platform as admin: " \
        /platforms \
        ${ADMIN_TOKEN} \
        POST \
        'name=chmoulebogosse|location=ParisEstMagique|contact=thecedric@isthegreatest.com|tenant_id=0000101010101'

curl_it "Get created platform as user: " \
        /platforms/ \
        ${USER_TOKEN} \
        GET \
        " " \
        "thecedric@isthegreatest.com"

curl_it "Delete created platform as admin: " \
        /platforms/chmoulebogosse \
        $ADMIN_TOKEN  \
        DELETE

echo "Done and successful :)"
