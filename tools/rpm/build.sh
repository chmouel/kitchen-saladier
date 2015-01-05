#!/bin/bash
set -exf

CURDIR=$(dirname $(readlink -f $0))
TOPDIR=$(git rev-parse --show-toplevel 2>/dev/null)
DATE_VERSION="0.0.$(date +%Y%m%d)git"

rm -rf ${CURDIR}/.build/rpm
mkdir -p ${CURDIR}/.build/rpm/{BUILD,SRPMS,SPECS,RPMS/noarch}
cp -r ${CURDIR}/SOURCES ${CURDIR}/.build/rpm

pushd ${TOPDIR} >/dev/null

COMMIT_VERSION=$(git rev-parse --short HEAD)

export PBR_VERSION=${DATE_VERSION}${COMMIT_VERSION}

python setup.py sdist --dist-dir ${CURDIR}/.build/rpm/SOURCES/ >/dev/null

[[ -e etc/saladier/saladier.conf.sample ]] || {
    echo "You need to generate the sample first with tox -egenconfig so we can copy it"
    exit 1
}

cp etc/saladier/saladier.conf.sample ${CURDIR}/.build/rpm/SOURCES/saladier.conf.sample

popd >/dev/null

sed -e "s/%define _version.*/%define _version ${PBR_VERSION}/" ${CURDIR}/SPECS/kitchen-saladier.spec > \
        ${CURDIR}/.build/rpm/SPECS/kitchen-saladier.spec

docker build -t chmouel/buildrpm ${CURDIR}
docker run -v $CURDIR/.build:/data -it chmouel/buildrpm

if [[ -n ${ARTIFACT_DIR} ]];then
    rm -rf ${ARTIFACT_DIR}/rpm
    cp -a ${CURDIR}/.build/output ${ARTIFACT_DIR}/rpm
    type -p createrepo >/dev/null && createrepo ${ARTIFACT_DIR}/rpm
fi
