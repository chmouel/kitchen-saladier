# -*- coding: utf-8 -*-
# Copyright (C) 2013 eNovance SAS <licensing@enovance.com>
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
from saladier.tests.api import utils
import saladier.tests.api.v1.base as base


class TestPlatforms(base.V1FunctionalTest):
    def setUp(self):
        super(TestPlatforms, self).setUp()

    def test_platform_create(self):
        platform_dict = dict(name="name1",
                             location="location1",
                             contact="platform@owner.org",
                             tenant_id="clarasoft")
        self.post_json("/platforms", platform_dict, status=201)

        data = self.get_json('/platforms/')
        self.assertEqual(1, len(data['platforms']))
        self.assertEqual('platform@owner.org', data['platforms'][0]['contact'])
        self.assertEqual('name1', data['platforms'][0]['name'])
        self.assertEqual('location1', data['platforms'][0]['location'])
        self.assertEqual('clarasoft', data['platforms'][0]['tenant_id'])

    def test_platform_create_user_denied(self):
        platform_dict = dict(name="name1",
                             location="location1",
                             contact="platform@owner.org",
                             tenant_id="clarasoft")
        self.post_json("/platforms", platform_dict,
                       headers={'X-Auth-Token': utils.MEMBER_TOKEN},
                       status=403)

    def test_platform_get_by_id(self):
        name = 'name1'
        platform_dict = dict(name=name,
                             location="location1",
                             contact="platform@owner.org",
                             tenant_id="clarasoft")
        self.post_json("/platforms", platform_dict)
        platform_id = self._get_platform_id(name)
        data = self.get_json('/platforms/' + platform_id)

        self.assertEqual('platform@owner.org', data['contact'])
        self.assertEqual(name, data['name'])
        self.assertEqual('location1', data['location'])
        self.assertEqual('clarasoft', data['tenant_id'])

    def test_platform_create_conflict(self):
        platform_dict = dict(name="name1",
                             location="location1",
                             contact="platform@owner.org",
                             tenant_id="clarasoft")
        self.post_json("/platforms", platform_dict, status=201)

        ret = self.post_json("/platforms", platform_dict, status=409)
        self.assertEqual(409, ret.status_int)

    def test_platform_create_notfound(self):
        self.get_json('/platforms/random', status=404)

    def test_platform_delete(self):
        name = "name1"
        platform_dict = dict(name=name,
                             location="location1",
                             contact="platform@owner.org",
                             tenant_id="clarasoft")
        self.post_json("/platforms", platform_dict, status=201)
        platform_id = self._get_platform_id(name)
        status = self.delete('/platforms/%s' % platform_id, status=204)
        self.assertEqual(204, status.status_int)

    def test_platform_delete_as_user(self):
        platform_dict = dict(name="name1",
                             location="location1",
                             contact="platform@owner.org",
                             tenant_id="clarasoft")
        self.post_json("/platforms", platform_dict, status=201)

        status = self.delete('/platforms/name1',
                             headers={'X-Auth-Token': utils.MEMBER_TOKEN},
                             expect_errors=True)
        self.assertEqual(403, status.status_int)
