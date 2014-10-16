#!/bin/bash

function exit_it() {
    [[ -d .testrepository ]] && { sudo chown -R $(id -u):$(id -g) .testrepository || : ; }
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
[[ -d .testrepository ]] && { sudo chown -R $(id -u):$(id -g) .testrepository || : ; }
fig run --rm unittests

# stupid testr (2)
[[ -d .testrepository ]] && { sudo chown -R $(id -u):$(id -g) .testrepository || : ; }
fig run --rm functional
