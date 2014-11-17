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
import saladier.tests.api.base as base
from saladier.tests.api import utils


class TestProducts(base.FunctionalTest):
    def setUp(self):
        super(TestProducts, self).setUp()

    def test_product_create(self):
        prod_dict = dict(name="name1",
                         team="team1",
                         contact="product@owner.org")
        self.post_json("/products/", prod_dict, status=201)

        data = self.get_json('/products/')
        self.assertEqual(1, len(data['products']))
        self.assertEqual('product@owner.org', data['products'][0]['contact'])
        self.assertEqual('name1', data['products'][0]['name'])
        self.assertEqual('team1', data['products'][0]['team'])

    def test_product_get_by_name(self):
        name = 'name1'
        prod_dict = dict(name=name,
                         team="team1",
                         contact="product@owner.org")
        self.post_json("/products/", prod_dict)

        data = self.get_json('/products/' + name)

        self.assertEqual('product@owner.org', data['contact'])
        self.assertEqual('name1', data['name'])
        self.assertEqual('team1', data['team'])

    def test_product_create_conflict(self):
        prod_dict = dict(name="name1",
                         team="team1",
                         contact="product@owner.org")
        self.post_json("/products/", prod_dict, status=201)

        prod_dict = dict(name="name1",
                         team="team1",
                         contact="product@owner.org")
        ret = self.post_json("/products/", prod_dict, status=409)
        self.assertEqual(409, ret.status_int)

    def test_product_create_notfound(self):
        self.get_json('/products/random', status=404)

    def test_product_delete(self):
        prod_dict = dict(name="name1",
                         team="team1",
                         contact="product@owner.org")
        self.post_json("/products/", prod_dict, status=201)

        status = self.delete('/products/name1', status=204)
        self.assertEqual(204, status.status_int)

    def test_product_delete_as_user(self):
        prod_dict = dict(name="name1",
                         team="team1",
                         contact="product@owner.org")
        self.post_json("/products/", prod_dict, status=201)

        status = self.delete('/products/name1',
                             headers={'X-Auth-Token': utils.MEMBER_TOKEN},
                             expect_errors=True)
        self.assertEqual(403, status.status_int)
