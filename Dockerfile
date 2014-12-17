# The best way to use that is to use fig in tools/container
# You can run it in standalone with :
# docker build -t saladier . # build image
# docker run -v .:/code --rm --it saladier # run it
# and inside container just do a pip install -e. to install saladier properly.
# really the best is to use fig which would build you a keystone+mariadb and connect
# the saladier to it
FROM fedora:21
MAINTAINER Chmouel Boudjnah <chmouel@enovance.com>
EXPOSE 8777

RUN useradd -s /bin/bash -G adm,wheel,systemd-journal -m saladier

RUN yum -y groupinstall 'Development Tools'
RUN yum -y install openssl
RUN yum -y install python-keystoneclient
RUN yum -y install python-virtualenv
RUN yum -y install libxslt-devel
RUN yum -y install mysql
RUN yum -y install python-tox
RUN yum -y install dnf-plugins-core
RUN yum -y install graphviz
RUN yum -y install postgresql
RUN yum -y install python-psycopg2
RUN yum -y install python3-psycopg2
RUN yum -y install postgresql-devel
RUN yum -y install python3-devel

RUN virtualenv /virtualenv
RUN chown -R saladier: /virtualenv
RUN mkdir -p /code

ADD requirements.txt /code/
ADD test-requirements.txt /code/

USER saladier
WORKDIR /code

RUN /virtualenv/bin/pip install -U -r requirements.txt -r test-requirements.txt
