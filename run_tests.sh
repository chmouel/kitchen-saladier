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

# Clean as much as possible before starting
clean_repo
fig ps -q|xargs -r docker stop || :
fig ps -q|xargs -r docker rm || :
{ docker images -q --filter "dangling=true" | xargs docker rmi ;} || true

# Unittests
fig run --rm unittests

# clean again cause without it we end up in a world of pain of conflicts and
# races.
clean_repo
fig ps -q|xargs -r docker stop || :
fig ps -q|xargs -r docker rm || :

# Functional
fig run functional

# Build rpms
clean_repo
./tools/rpm/build.sh
