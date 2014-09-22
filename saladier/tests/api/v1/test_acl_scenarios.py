#
# Copyright 2012 New Dream Network, LLC (DreamHost)
#
# Author: Julien Danjou <julien@danjou.info>
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
"""Test ACL."""

import datetime
import json

import six
import testtools
import webtest

from saladier.api import app
from saladier.openstack.common import timeutils
from saladier.tests import api as acl
from saladier.tests.api import v1

VALID_TOKEN = '4562138218392831'
VALID_TOKEN2 = '4562138218392832'


class FakeMemcache(object):
    @staticmethod
    def get(key):
        if key == "tokens/%s" % VALID_TOKEN:
            dt = timeutils.utcnow() + datetime.timedelta(minutes=5)
            return json.dumps(({'access': {
                'token': {'id': VALID_TOKEN,
                          'expires': timeutils.isotime(dt)},
                'user': {
                    'id': 'user_id1',
                    'name': 'user_name1',
                    'tenantId': '123i2910',
                    'tenantName': 'mytenant',
                    'roles': [
                        {'name': 'admin'},
                    ]},
            }}, timeutils.isotime(dt)))
        if key == "tokens/%s" % VALID_TOKEN2:
            dt = timeutils.utcnow() + datetime.timedelta(minutes=5)
            return json.dumps(({'access': {
                'token': {'id': VALID_TOKEN2,
                          'expires': timeutils.isotime(dt)},
                'user': {
                    'id': 'user_id2',
                    'name': 'user-good',
                    'tenantId': 'project-good',
                    'tenantName': 'goodies',
                    'roles': [
                        {'name': 'Member'},
                    ]},
            }}, timeutils.isotime(dt)))

    @staticmethod
    def set(key, value, **kwargs):
        pass


class TestAPIACL(v1.FunctionalTest):

    def setUp(self):
        super(TestAPIACL, self).setUp()
        self.environ = {'fake.cache': FakeMemcache()}

    def get_json(self, path, expect_errors=False, headers=None,
                 q=None, **params):
        return super(TestAPIACL, self).get_json(path,
                                                expect_errors=expect_errors,
                                                headers=headers,
                                                q=q or [],
                                                extra_environ=self.environ,
                                                **params)

    def _make_app(self):
        self.CONF.set_override("cache", "fake.cache", group=acl.OPT_GROUP_NAME)
        file_name = self.path_get('etc/saladier/api_paste.ini')
        self.CONF.set_override("api_paste_config", file_name)
        return webtest.TestApp(app.load_app())

    def test_not_found_app_config(self):
        file_name = self.path_get('/NOTFOUND')
        self.CONF.set_override("api_paste_config", file_name)
        self.assertRaises(app.APIPasteNotFound, app.load_app)

    @testtools.skipIf(six.PY3, reason="Skip on py3 until lp:1372484 is sorted")
    def test_non_authenticated(self):
        response = self.get_json('/meters', expect_errors=True)
        self.assertEqual(401, response.status_int)

    @testtools.skipIf(six.PY3, reason="Skip on py3 until lp:1372484 is sorted")
    def test_authenticated_wrong_role(self):
        response = self.get_json('/',
                                 expect_errors=True,
                                 headers={
                                     "X-Roles": "Member",
                                     "X-Tenant-Name": "admin",
                                     "X-Project-Id":
                                     "bc23a9d531064583ace8f67dad60f6bb",
                                 })
        self.assertEqual(401, response.status_int)

    def test_authenticated(self):
        data = self.get_json('/test/',
                             headers={"X-Auth-Token": VALID_TOKEN,
                                      "X-Roles": "admin",
                                      "X-Tenant-Name": "admin",
                                      "X-Project-Id":
                                      "bc23a9d531064583ace8f67dad60f6bb",
                                      })
        # TODO(chmou): Change with a proper call when needed
        self.assertIn('foo', data)
