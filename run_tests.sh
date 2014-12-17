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

# NOTE(chmou): launch unittests at the end this is needed for condition to success
clean_repo

fig ps -q|xargs -r docker stop || :
fig ps -q|xargs -r docker rm || :
fig run --rm unittests

# stupid testr (2)
clean_repo
fig ps -q|xargs -r docker stop || :
fig ps -q|xargs -r docker rm || :
fig run functional
