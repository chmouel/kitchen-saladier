#!/bin/bash
set -ex

function check_up() {
    service=$1
    host=$2
    port=$3

    # check that the saladier is up
    while true;do
        python -c "import socket;s = socket.socket(socket.AF_INET, socket.SOCK_STREAM);s.connect(('$host', $port))" >/dev/null 2>/dev/null && break || echo "Waiting that $service on ${SALADIER_PORT_8777_TCP_ADDR}:8777 is started (sleeping for 5)"
        sleep 5
    done

}

check_up saladier ${SALADIER_PORT_8777_TCP_ADDR} 8777
check_up keystone ${KEYSTONE_PORT_35357_TCP_ADDR} 35357

TOKEN=$(curl -s -X POST http://${KEYSTONE_PORT_35357_TCP_ADDR}:35357/v2.0/tokens -H "Content-Type: application/json" \
             -d '{"auth": {"tenantName": "service", "passwordCredentials": {"username": "saladier", "password": "password"}}}' |
            python -c 'import sys, json; print json.load(sys.stdin)["access"]["token"]["id"]')

# This is my only unittest for now we will expand with a proper unittest
# framework in the future when REST class will be written. (The -f to curl would
# exit 1 if we have a 4xx or 5xx errors)
curl -s -L -f -H "x-auth-token: ${TOKEN}" http://${SALADIER_PORT_8777_TCP_ADDR}:8777/v1/test
