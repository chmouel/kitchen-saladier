============
Contributing
============

.. highlight:: bash

.. include:: ../../CONTRIBUTING.rst


Testing
=======

Since the `Saladier` is using keystone you need a keystone for that.

You can build a devstack with only keystone, which should be pretty light. When you have checked out your devstack, just add this to your localrc ::

  ENABLED_SERVICES=key,mysql

and run `./stack.sh` to get you a minimal devstack with only keystone.

Here is some steps to easily get started::

  tox -epy27
  cat <<EOF>etc/saladier/saladier.conf.sample

  [DEFAULT]
  api_paste_config=etc/saladier/api_paste.ini
  debug = True

  [keystone_authtoken]
  signing_dir = /tmp/saladier-signing-dir
  admin_tenant_name = service
  admin_password = ADMIN
  admin_user = admin
  identity_uri = http://localhost:35357
  EOF

  # Launch the server
  ./.tox/py27/bin/saladier-api --config-file etc/saladier/saladier.conf.sample

Now you have your `Saladier` running, you need to get a token from
keystone to be able to do that, I (chmouel) have a script to automate
this, just do the following the steps::

  mkdir -p ~/bin/
  curl -O ~/bin/ks https://gist.githubusercontent.com/chmouel/5001515/raw/ks.sh
  chmod +x ~/bin/ks

  # This is where the magic hapenning, it will get a token from
  # keystone and set it up in the shell variable $TOKEN
  eval $(~/bin/ks -s localhost)

  # Now you can use it to query the saladier to whatever URL
  curl -H "x-auth-token: $TOKEN" http://localhost:8777/
