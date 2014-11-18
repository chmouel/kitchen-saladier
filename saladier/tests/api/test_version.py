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
from oslo.config import cfg

import saladier.tests.api.base as base
import saladier.version


class TestVersion(base.FunctionalTest):
    def setUp(self):
        super(TestVersion, self).setUp()

        self.location = 'Alaska'
        self.provider = 'Pengouins'
        # NOTE(chmou): should figure out how we can use fixtures properly,
        # doesn't seem to work if i put them in conf_fixtures and does it
        # really matter to spend too mcuh time on it, cause that probably never
        # conflicts, like ever!!!! (Trademark pending)
        cfg.CONF.set_override('location', self.location,
                              group='api')
        cfg.CONF.set_override('provider', self.provider,
                              group='api')

    def test_version(self):
        data = self.get_json('/', path_prefix='', status=200)
        self.assertEqual(self.location, data['location'])
        self.assertEqual(self.provider, data['provider'])
        self.assertEqual(saladier.version.version_info.release_string(),
                         data['version'])
