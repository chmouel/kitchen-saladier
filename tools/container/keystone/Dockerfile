FROM kollaglue/fedora-rdo-base
MAINTAINER Chmouel Boudjnah <chmouel@chmouel.com>

#Install required packages
RUN yum install -y openstack-keystone \
    openstack-utils \
    mariadb \
    && yum clean all

ADD ./start.sh /start.sh

EXPOSE 5000 35357

CMD ["/start.sh"]
