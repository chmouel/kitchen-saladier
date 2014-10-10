#!/bin/bash
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

pushd tools/container/ >/dev/null && {
    fig run --rm unittests
    fig run --rm functional
} && popd >/dev/null

# stupid testr
chown -R $USER: .testrepository/
