# -*- encoding: utf-8 -*-
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.
"""
Tests for ACL. Checks whether certain kinds of requests
are blocked or allowed to be processed.
"""

# NOTE(deva): import auth_token so we can override a config option
from keystonemiddleware import auth_token  # noqa
from oslo.config import cfg

from saladier.tests.api import base
from saladier.tests.api import utils


class TestACL(base.FunctionalTest):
    def setUp(self):
        super(TestACL, self).setUp()
        self.environ = {'fake.cache': utils.FakeMemcache()}

    def get_json(self, path, expect_errors=False, headers=None, q=[], **param):
        return super(TestACL, self).get_json(
            path, expect_errors=expect_errors,
            headers=headers, q=q,
            extra_environ=self.environ, **param)

    def _make_app(self):
        cfg.CONF.set_override('cache', 'fake.cache',
                              group='keystone_authtoken')
        return super(TestACL, self)._make_app(enable_acl=True)

    def test_non_authenticated(self):
        response = self.get_json('/products/', expect_errors=True)
        self.assertEqual(401, response.status_int)

    def test_authenticated(self):
        response = self.get_json(
            "/products/", headers={'X-Auth-Token': utils.ADMIN_TOKEN})
        self.assertEqual({'products': []}, response)

    def test_public_api(self):
        # expect_errors should be set to True: If expect_errors is set to False
        # the response gets converted to JSON and we cannot read the response
        # code so easy.
        response = self.get_json("/",
                                 path_prefix='', expect_errors=True)
        self.assertEqual(200, response.status_int)
