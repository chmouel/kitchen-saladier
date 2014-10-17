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
    source .tox/run_tests/bin/activate

    # Until there is a proper release with the fixes we want
    pip install -U https://github.com/docker/fig/zipball/872a1b5a5c29f21ea399dab927a8d5afcd56257d
else
    source .tox/run_tests/bin/activate
fi

# stupid testr (1)
clean_repo
fig run --rm unittests

# stupid testr (2)
clean_repo
fig run --rm functional
