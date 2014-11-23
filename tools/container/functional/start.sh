#!/bin/bash
set -e
CURL_FLAG="-s"
DOCDIR=$(readlink -f $(dirname $(readlink -f $0))/../../../doc/source/rests/)

[[ -n ${DEBUG} ]] && set -x
[[ -n ${DEBUG} ]] && CURL_FLAG="-i"

GENERATE_DOC_RESTS=${GENERATE_DOC_RESTS:-""}

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

function curl_it {
    local msg=$1
    local type=$2
    local url=$3
    local token=$4
    local method=$5
    local datas=$6
    local grep=$7

    local _curl_datas=""
    [[ ${datas} == " " ]] && datas= # NOTE(chmou): placeholders when we don't want to go on with the arg
    [[ ${url} == / ]] && furl=http://${SALADIER_PORT_8777_TCP_ADDR}:8777/ || furl=http://${SALADIER_PORT_8777_TCP_ADDR}:8777/v1${url}

    [[ ${token} != " " ]] && gtoken="-H x-auth-token:${token}" || gtoken=""

    for x in ${datas//|/ };do
        _curl_datas="${_curl_datas} -d $x"
    done

    echo -n "$msg: "
    curl -f -i -o /tmp/output.json ${CURL_FLAG} ${_curl_datas} -L -X ${method} ${gtoken} ${furl} || failed=$?

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

    [[ -z ${GENERATE_DOC_RESTS} ]] && return

    rm -f ${DOCDIR}/${type}.rst

    str="${method} ${url}"
    # NOTE(chmou): make it pretty user_tenant_id
    [[ ${str} == *${USER_TENANT_ID}* ]] && str=${str/${USER_TENANT_ID}/tenantId}

    echo ${str} >> ${DOCDIR}/${type}.rst
    printf %${#str}s |tr " " "=" >> ${DOCDIR}/${type}.rst
    echo -e "\n\n${msg}\n\n" >> ${DOCDIR}/${type}.rst

    if [[ ${method} == "POST" ]];then
        echo -e "Arguments::\n\n  {" >> ${DOCDIR}/${type}.rst
        for x in ${datas//|/ };do
            echo -e "    \"${x%=*}\": \"${x#*=}\"," >> ${DOCDIR}/${type}.rst
        done
        echo -e "  }\n" >> ${DOCDIR}/${type}.rst
    fi

    echo -e "Returns::\n" >> ${DOCDIR}/${type}.rst
    sed -n -e '1s,HTTP/1.0 ,    ,p;' /tmp/output.json|tr -d '' >> ${DOCDIR}/${type}.rst
    echo -e "\n\n" >> /tmp/${type}.rst

    if [[ ${method} == "GET" ]];then
        sed '1,/^\r$/d' /tmp/output.json | python -mjson.tool |sed -n -e 's/^/    /p' >> ${DOCDIR}/${type}.rst
    fi

    if [[ ${token} == ${ADMIN_TOKEN} ]];then
            cat <<EOF>>${DOCDIR}/${type}.rst

.. note:: This call needs to be made with the ``admin`` rights.
EOF
    fi
}

# NOTE(chmou): This is our blackbox functest suite with curl for now we will
# expand with a proper framework (i.e: tempest-lib) in the future when REST
# class will be written. (The -f to curl would exit 1 if we have a 4xx or 5xx
# errors)

curl_it "Get saladier public URL with version and location" \
        public_version_access \
        / \
        " " \
        GET \
        " " \
        "Paris"

# Create a product
curl_it "Create product" \
         product_create \
         /products \
         ${ADMIN_TOKEN} \
         POST \
         "team=boa|name=product1|contact=cedric@isthegreatest.com"


curl_it "Associate a product to a version" \
        product_version_create \
        /versions \
        ${ADMIN_TOKEN} \
        POST \
        'product=product1|url=http://anywhereyoulike|version=1.0'

curl_it "Subscribe tenant ${USER_NAME} to product" \
        product_subscription_create \
        /subscriptions \
        ${ADMIN_TOKEN} \
        POST \
        "product_name=product1|tenant_id=${USER_TENANT_ID}"

curl_it "List products available for the current users" \
        product_list \
        /products/ \
        ${USER_TOKEN} \
        GET \
        " " \
        "product1"

curl_it "Show specific product information and validations" \
        product_get \
        /products/product1 \
        ${USER_TOKEN} \
        GET \
        " " \
        "cedric@isthegreatest.com"

curl_it "Show specific product/version information and validations" \
        product_get_version \
        /products/product1/1.0 \
        ${USER_TOKEN} \
        GET \
        " " \
        "validated_on"

curl_it "Delete subscription of ${USER_NAME} to our product" \
        product_subscription_delete \
        /subscriptions/product1/${USER_TENANT_ID} \
        ${ADMIN_TOKEN} \
        DELETE

curl_it "Delete Association between product and version" \
        product_version_delete \
        /versions/product1/1.0 \
        ${ADMIN_TOKEN} \
        DELETE

curl_it "Delete created product" \
        product_delete \
        /products/product1 \
        ${ADMIN_TOKEN} \
        DELETE

curl_it "Create platform" \
        platform_create \
        /platforms \
        ${ADMIN_TOKEN} \
        POST \
        'name=platform1|location=ParisEstMagique|contact=thecedric@isthegreatest.com|tenant_id=0000101010101'

curl_it "Show created platform" \
        platform_list \
        /platforms/ \
        ${USER_TOKEN} \
        GET \
        " " \
        "thecedric@isthegreatest.com"

curl_it "Delete created platform" \
        platform_delete \
        /platforms/platform1 \
        $ADMIN_TOKEN  \
        DELETE

echo "Done and successful :)"
