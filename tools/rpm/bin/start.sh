#!/bin/bash
# script run inside the container
rpmbuild -ba rpmbuild/SPECS/kitchen-saladier.spec || exit 1

[[ -d /data ]] || exit 0

sudo rm -rf /data/output
sudo cp -a rpmbuild/RPMS/noarch /data/output
