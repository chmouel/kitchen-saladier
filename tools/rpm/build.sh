#!/bin/bash
set -exf

CURDIR=$(dirname $(readlink -f $0))
TOPDIR=$(git rev-parse --show-toplevel 2>/dev/null)

rm -rf ${CURDIR}/.build/rpm
mkdir -p ${CURDIR}/.build/rpm/{BUILD,SRPMS,SPECS,RPMS/noarch}
cp -r ${CURDIR}/SOURCES ${CURDIR}/.build/rpm

pushd ${TOPDIR} >/dev/null
python setup.py sdist --dist-dir ${CURDIR}/.build/rpm/SOURCES/
SALADIER_VERSION=$(sed -n '/^Version/ { s/.* //; p}' kitchen_saladier.egg-info/PKG-INFO)
popd >/dev/null

sed -e "s/%define _version.*/%define _version ${SALADIER_VERSION}/" ${CURDIR}/SPECS/kitchen-saladier.spec > \
        ${CURDIR}/.build/rpm/SPECS/kitchen-saladier.spec

docker build -t chmouel/buildrpm ${CURDIR}
docker run -v $CURDIR/.build:/data -it chmouel/buildrpm

if [[ -n ${ARTIFACT_DIR} ]];then
    rm -rf ${ARTIFACT_DIR}/rpm
    cp -a ${CURDIR}/.build/output ${ARTIFACT_DIR}/rpm
    type -p createrepo >/dev/null && createrepo ${ARTIFACT_DIR}/rpm
fi
