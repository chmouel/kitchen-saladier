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

type -p fig >/dev/null || {
    echo "You need to have fig installed. Just yum -y install fig"
    exit 1
}

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

# Build rpms
clean_repo
./tools/rpm/build.sh
