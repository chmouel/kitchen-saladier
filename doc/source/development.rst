=================
Development setup
=================

Setup Keystone service
----------------------

The Saladier is using Keystone for authentication so you would need to deploy
one for your development setup. This is done through the use of a minimal
Devstack with just the Keystone service, here are the steps:

.. code-block:: bash

   $ git clone https://github.com/openstack-dev/devstack.git
   $ cd devstack
   $ cat <<EOF>localrc

     ENABLED_SERVICES=key,mysql

     DATABASE_PASSWORD=password
     SERVICE_TOKEN=password
     SERVICE_PASSWORD=password
     ADMIN_PASSWORD=password
     EOF
   $ stack.sh

We now have a devstack with Keystone running, say it runs on 192.168.122.5 for
this example (it should be another address in your configuration).

Installing the Saladier
-----------------------

First we install the Saladier for development purpose:

.. code-block:: bash

   $ python setup.py develop

Configuring the Saladier
------------------------

To configure the Saladier we need to edit its configuration file:

.. code-block:: bash

   $ cd saladier
   $ cat <<EOF>etc/saladier/saladier.conf.sample

     [DEFAULT]
     api_paste_config=etc/saladier/api_paste.ini
     debug = True

     [keystone_authtoken]
     signing_dir = /tmp/saladier-signing-dir
     admin_tenant_name = service
     admin_password = ADMIN
     admin_user = admin
     identity_uri = http://192.168.122.5:35357
     EOF

Launch the Saladier API server
------------------------------

To launch the server api, you can use the saladier-api command:

.. code-block:: bash

   $ saladier-api --config-file etc/saladier/saladier.conf.sample

The saladier will now be running on http://localhost:8777  by default.

Before starting to send requests to the saladier, we need to generate a
keystone token.

You first need to install the keystone client:

.. code-block:: bash

   $ pip install python-keystoneclient

The OS_* environment variables should be set as described in OpenStack
documentation, cf. http://docs.openstack.org/user-guide/content/cli_openrc.html

.. code-block:: bash

   $ export OS_AUTH_URL=http://192.168.122.71:5000/v2.0/
   $ export OS_USERNAME=admin
   $ export OS_PASSWORD=password
   $ export OS_TENANT_NAME=demo

You can get a token in the TOKEN variable with this one-liner:

.. code-block:: bash

   $ TOKEN=$(keystone token-get| grep ' id'| cut -d'|' -f 3| tr -d '[:space:]')

Or just copy it from the output of 'keystone token-get'

Now you can use it to query the saladier to whatever URL.

.. code-block:: bash

   $ curl -H "x-auth-token: $TOKEN" http://localhost:8777/

You development setup is done ! Congratulations :) !

Unit Testing
------------

The unit tests is by default tighted to the database so you need to have a mysql
database running locally with the user root being able to access to the saladier
database without password.

We have added a docker based container for our CI to make things very
easy. We have as well added a run_tests.sh to make it easy to launch those, 
This is the manual steps that the run_tests.sh script is doing

- Install docker on your laptop, for example on fedora::

    yum -y install docker-io

- Install `fig` with ::

    pip install -U fig

- Go to `tools/containers` inside the saladier repository and just type::

    fig run unittests

It will setup a mysql and mount your saladier code as volume to launch the
unittests with mysql. The first time should take a bit of time to construct the
images but after that it should quick as the light :)

 This is currently only run on py2
