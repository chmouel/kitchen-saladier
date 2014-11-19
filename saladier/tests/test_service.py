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
import mock
import oslo.config

import saladier.service
from saladier.tests.api import base


class TestService(base.FunctionalTest):
    @mock.patch.object(oslo.config.cfg, "CONF")
    def test_service(self, mcfg):
        # NOTE(chmou): --debug would be grubbed and --version would stay
        saladier.service.prepare_service(['--debug', '--version'])
        mcfg.assert_called_with(['--version'], project='saladier')

        with mock.patch('sys.argv', ['--debug', '--version']):
            saladier.service.prepare_service()
            mcfg.assert_called_with(['--version'], project='saladier')
