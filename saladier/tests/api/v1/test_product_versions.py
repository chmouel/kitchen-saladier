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
import saladier.tests.api.base as base
from saladier.tests.api import utils


class TestProductVersions(base.FunctionalTest):
    def setUp(self):
        super(TestProductVersions, self).setUp()

    def test_product_version_create(self):
        prod_dict = dict(name="name1",
                         team="team1",
                         contact="product@owner.org")
        self.post_json("/products/", prod_dict, status=201)

        for version in ['1.0', '1.1']:
            version_dict = dict(product="name1",
                                url="http://localhost/",
                                version=version)
            self.post_json("/versions/", version_dict, status=201)

    def test_product_version_delete(self):
        prod_dict = dict(name="name1",
                         team="team1",
                         contact="product@owner.org")
        self.post_json("/products/", prod_dict, status=201)

        version_dict = dict(product="name1",
                            url="http://localhost/",
                            version="1.0")
        self.post_json("/versions/", version_dict, status=201)
        self.delete('/versions/name1/1.0', status=204)

    def test_product_version_delete_as_user(self):
        prod_dict = dict(name="name1",
                         team="team1",
                         contact="product@owner.org")
        self.post_json("/products/", prod_dict, status=201)

        version_dict = dict(product="name1",
                            url="http://localhost/",
                            version="1.0")
        self.post_json("/versions/", version_dict, status=201)

        self.delete('/versions/name1/1.0',
                    headers={'X-Auth-Token': utils.MEMBER_TOKEN},
                    status=403)

    def test_product_version_listing(self):
        prod_dict = dict(name="name1",
                         team="team1",
                         contact="product@owner.org")
        self.post_json("/products/", prod_dict, status=201)

        for version in ['1.0', '1.1']:
            version_dict = dict(product="name1",
                                url="http://localhost/",
                                version=version)
            self.post_json("/versions/", version_dict, status=201)
        data = self.get_json('/versions/name1', status=200)
        self.assertEqual(2, len(data['versions']))
