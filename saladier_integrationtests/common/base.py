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
from saladier_integrationtests.common import clients
from saladier_integrationtests.common import config

import testtools


class Base(testtools.TestCase):

    def setUp(self):
        super(Base, self).setUp()

        self.conf = config.init_conf(True)

        self.assertIsNotNone(self.conf.auth_url,
                             'No auth_url configured')

        self.assertIsNotNone(self.conf.user_name,
                             'No username configured')
        self.assertIsNotNone(self.conf.user_password,
                             'No password configured')
        self.assertIsNotNone(self.conf.user_tenant_name,
                             'No tenant configured')

        self.assertIsNotNone(self.conf.admin_name,
                             'No admin username configured')
        self.assertIsNotNone(self.conf.admin_password,
                             'No admin password configured')
        self.assertIsNotNone(self.conf.admin_tenant_name,
                             'No admin tenant configured')

        self.manager = clients.ClientManager(self.conf)
        self.user_client = self.manager.user_client
        self.admin_client = self.manager.admin_client
