# The best way to use that is to use fig in tools/container
# You can run it in standalone with :
# docker build -t saladier . # build image
# docker run -v .:/code --rm --it saladier # run it
# and inside container just do a pip install -e. to install saladier properly.
# really the best is to use fig which would build you a keystone+mariadb and connect
# the saladier to it
FROM fedora:20
MAINTAINER Chmouel Boudjnah <chmouel@enovance.com>
EXPOSE 8777

RUN useradd -s /bin/bash -G adm,wheel,systemd-journal -m saladier
RUN sed -i.bak -n -e '/^Defaults.*requiretty/ { s/^/# /;};/^%wheel.*ALL$/ { s/^/# / ;} ;/^#.*wheel.*NOPASSWD/ { s/^#[ ]*//;};p' /etc/sudoers
RUN yum -y groupinstall 'Development Tools'
RUN yum -y install openssl python-keystoneclient python-virtualenv libxslt-devel mysql python-tox dnf-plugins-core

RUN dnf -y copr enable hguemar/python34-fedora20
RUN yum -y install python34-devel

RUN virtualenv /virtualenv 
RUN chown -R saladier: /virtualenv
RUN mkdir -p /code

ADD requirements.txt /code/
ADD test-requirements.txt /code/

USER saladier
WORKDIR /code

RUN /virtualenv/bin/pip install -U -r requirements.txt -r test-requirements.txt
