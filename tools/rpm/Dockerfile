FROM fedora:21
MAINTAINER Chmouel Boudjnah <chmouel@enovance.com>

RUN yum -y groupinstall 'Development Tools'
RUN yum -y install fedora-packager
RUN yum -y install yum-utils

RUN yum -y install sudo
RUN sed -i.bak -n -e '/^Defaults.*requiretty/ { s/^/# /;};/^%wheel.*ALL$/ { s/^/# / ;} ;/^#.*wheel.*NOPASSWD/ { s/^#[ ]*//;};p' /etc/sudoers

RUN yum install -y https://rdo.fedorapeople.org/rdo-release.rpm

RUN useradd -s /bin/bash -G adm,wheel,systemd-journal -m saladier

WORKDIR /home/saladier
CMD /start.sh

ADD bin/start.sh /start.sh

ADD .build/rpm/ /home/saladier/rpmbuild/
RUN chown -R saladier: /home/saladier
RUN yum-builddep -y rpmbuild/SPECS/kitchen-saladier.spec

USER saladier
