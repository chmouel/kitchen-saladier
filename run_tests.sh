#!/bin/bash
set -ex

function clean_repo() {
    # Since we are writting as root let fix the perms
    sudo chown -R $(id -u):$(id -g) ./ || :
}

function exit_it() {
    clean_repo
}
trap exit_it EXIT

set -ex

if [[ ! -d .tox/run_tests ]];then
    mkdir -p .tox
    virtualenv .tox/run_tests
fi

source .tox/run_tests/bin/activate
pip install -U fig

# stupid testr (1)
clean_repo
fig run --rm unittests

# stupid testr (2)
clean_repo
fig stop keystone
fig stop saladier
fig start keystone
fig start saladier
fig run functional
