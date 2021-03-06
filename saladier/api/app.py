# -*- coding: utf-8 -*-
# Copyright (C) 2014 eNovance SAS <licensing@enovance.com>
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.
import logging
import os
import socket
from wsgiref import simple_server

import netaddr
from oslo.config import cfg
from paste import deploy
import pecan

from saladier.api import acl
from saladier.api import config as api_config
from saladier.api import hooks
from saladier.api import middleware
import saladier.db as db
from saladier.openstack.common import log


LOG = log.getLogger(__name__)


class APIPasteNotFound(Exception):
    pass


def get_pecan_config():
    # Set up the pecan configuration
    filename = api_config.__file__.replace('.pyc', '.py')
    return pecan.configuration.conf_from_file(filename)


def setup_app(pecan_config=None, extra_hooks=None):
    app_hooks = [hooks.ConfigHook(),
                 hooks.DBHook(db.get_connection(cfg.CONF)),
                 hooks.ContextHook(pecan_config.app.acl_public_routes),
                 ]
    if extra_hooks:
        app_hooks.extend(extra_hooks)

    if not pecan_config:
        pecan_config = get_pecan_config()

    pecan.configuration.set_config(dict(pecan_config), overwrite=True)

    app = pecan.make_app(
        pecan_config.app.root,
        static_root=pecan_config.app.static_root,
        template_path=pecan_config.app.template_path,
        debug=False,
        force_canonical=getattr(pecan_config.app, 'force_canonical', True),
        hooks=app_hooks,
        wrap_app=middleware.ParsableErrorMiddleware,
        guess_content_type_from_ext=False
    )

    if pecan_config.app.enable_acl:
        return acl.install(app, cfg.CONF, pecan_config.app.acl_public_routes)

    return app


class VersionSelectorApplication(object):
    def __init__(self):
        pc = get_pecan_config()
        pc.app.enable_acl = True
        self.v1 = setup_app(pecan_config=pc)

    def __call__(self, environ, start_response):
        return self.v1(environ, start_response)


def get_server_cls(host):
    """Return an appropriate WSGI server class base on provided host

    :param host: The listen host for the saladier API server.
    """
    server_cls = simple_server.WSGIServer
    if netaddr.valid_ipv6(host):
        # NOTE(dzyu) make sure use IPv6 sockets if host is in IPv6 pattern
        if getattr(server_cls, 'address_family') == socket.AF_INET:
            class server_cls(server_cls):
                address_family = socket.AF_INET6
    return server_cls


def get_handler_cls():
    return simple_server.WSGIRequestHandler


def load_app():
    # Build the WSGI app
    cfg_file = cfg.CONF.api.api_paste_config
    LOG.info("WSGI config requested: %s" % cfg_file)
    if not os.path.exists(cfg_file):
        raise APIPasteNotFound('api_paste_config file not found')
    LOG.info("Full WSGI config used: %s" % os.path.abspath(cfg_file))
    return deploy.loadapp("config:" + os.path.abspath(cfg_file))


def build_server(app=None):
    app = app or load_app()
    # Create the WSGI server and start it
    # host, port = cfg.CONF.api.host, cfg.CONF.api.port
    host, port = cfg.CONF.api.host, cfg.CONF.api.port
    server_cls = get_server_cls(host)

    srv = simple_server.make_server(host, port, app,
                                    server_cls, get_handler_cls())

    LOG.info('Starting server in PID %s', os.getpid())
    LOG.info("Configuration:")
    cfg.CONF.log_opt_values(LOG, logging.INFO)

    if host == '0.0.0.0':
        LOG.info((
            'serving on 0.0.0.0:%(sport)s, view at http://127.0.0.1:%(vport)s')
            % ({'sport': port, 'vport': port}))
    else:
        LOG.info(("serving on http://%(host)s:%(port)s") % (
                 {'host': host, 'port': port}))

    return srv


def app_factory(global_config, **local_conf):
    return VersionSelectorApplication()
