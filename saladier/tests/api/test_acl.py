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
import keystonemiddleware.auth_token
import mock

# NOTE(deva): import auth_token so we can override a config option
from keystonemiddleware import auth_token  # noqa

from saladier.tests.api import base
from saladier.tests.api import utils


class TestACL(base.FunctionalTest):
    @mock.patch.object(keystonemiddleware.auth_token.AuthProtocol,
                       '_reject_auth_headers', return_value=())
    def test_non_authenticated(self, m):
        response = self.get_json('/products/',
                                 headers={'X-Auth-Token': ''},
                                 expect_errors=True)
        self.assertEqual(401, response.status_int)

    def test_authenticated(self):
        prod_dict = dict(name="name1",
                         team="team1",
                         contact="product@owner.org")
        response = self.post_json("/products/", prod_dict,
                                  expect_errors=True)
        self.assertEqual(201, response.status_int)

    def test_non_admin(self):
        prod_dict = dict(name="name1",
                         team="team1",
                         contact="product@owner.org")
        response = self.post_json("/products/", prod_dict,
                                  headers={'X-Auth-Token': utils.MEMBER_TOKEN},
                                  expect_errors=True)
        self.assertEqual(403, response.status_int)

    def test_public_api(self):
        # expect_errors should be set to True: If expect_errors is set to False
        # the response gets converted to JSON and we cannot read the response
        # code so easy.
        response = self.get_json("/",
                                 headers={'X-Auth-Token': ''},
                                 path_prefix='', expect_errors=True)
        self.assertEqual(200, response.status_int)
