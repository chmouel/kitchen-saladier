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
import random
import socket

import mock
import oslo.config

import saladier.api.app as app
from saladier.tests.api import base


class TestApp(base.FunctionalTest):
    @mock.patch.object(oslo.config.cfg.CONF, "log_opt_values")
    def test_run_app(self, m):
        random_port = random.randrange(1024, 65536)
        oslo.config.cfg.CONF.set_override('port', random_port,
                                          group='api')
        oslo.config.cfg.CONF.set_override('host', '127.0.0.1',
                                          group='api')

        d = app.build_server(self._make_app())
        self.assertEqual(('127.0.0.1', random_port), d.server_address)

    def test_get_server_cls_ipv4(self):
        host = '127.0.0.1'
        self.assertEqual(socket.AF_INET,
                         app.get_server_cls(host).address_family)

    def test_get_server_cls_ipv6(self):
        host = '::1'
        self.assertEqual(socket.AF_INET6,
                         app.get_server_cls(host).address_family)
