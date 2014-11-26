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


class TestProducts(base.V1FunctionalTest):
    def setUp(self):
        super(TestProducts, self).setUp()

    def test_product_version_create_list(self):
        product_name = 'test_product_version_create_list'
        product_name2 = 'test_product_version_create_list2'

        self._create_sample_product(name=product_name)
        self._create_sample_product(name=product_name2)

        for version in base.SAMPLE_JSON_PRODUCTS['products']['name1']:
            self._create_sample_product_version(product=product_name,
                                                version=version)
        for version in base.SAMPLE_JSON_PRODUCTS['products']['name2']:
            self._create_sample_product_version(product=product_name2,
                                                version=version)

        data = self.get_json('/products/')['products'][product_name]
        self.assertEqual(base.SAMPLE_JSON_PRODUCTS['products']['name1'], data)

        data = self.get_json('/products/')['products'][product_name2]
        self.assertEqual(base.SAMPLE_JSON_PRODUCTS['products']['name2'], data)

    def test_product_get_by_name_has_versions(self):
        name = 'test_product_get_by_name_has_versions'
        self._create_sample_product(name=name)

        for version in base.SAMPLE_JSON_PRODUCTS['products']['name1']:
            self._create_sample_product_version(product=name,
                                                version=version)

        self.assertEqual(base.SAMPLE_JSON_PRODUCTS_NAME,
                         self.get_json('/products/' + name))

    def test_product_get_by_name_no_version(self):
        name = 'test_product_get_by_name_no_version'
        self._create_sample_product(name=name)

        ret_dict = {'versions': {},
                    'contact': base.SAMPLE_JSON_PRODUCTS_NAME['contact'],
                    'team': base.SAMPLE_JSON_PRODUCTS_NAME['team']}
        self.assertEqual(ret_dict, self.get_json('/products/' + name))

    def test_product_get_by_name_and_version(self):
        product_name = 'test_product_get_by_name_and_version'
        version = '1.0'

        self._create_sample_product(name=product_name)
        for version in base.SAMPLE_JSON_PRODUCTS['products']['name1']:
            self._create_sample_product_version(product=product_name,
                                                version=version)

        ret_dict = base.SAMPLE_JSON_PRODUCTS_NAME['versions'][version]
        self.assertEqual(ret_dict,
                         self.get_json('/products/%s/%s' %
                                       (product_name, version)))

    def test_product_create_conflict(self):
        product_name = 'test_product_create_conflict'
        prod_dict = dict(name=product_name,
                         team="team1",
                         contact="product@owner.org")
        self.post_json("/products", prod_dict, status=201)

        prod_dict = dict(name=product_name,
                         team="team1",
                         contact="product@owner.org")
        ret = self.post_json("/products", prod_dict, status=409)
        self.assertEqual(409, ret.status_int)

    def test_product_create_notfound(self):
        self.get_json('/products/random', status=404)

    def test_product_delete(self):
        product_name = 'test_product_delete'
        prod_dict = dict(name=product_name,
                         team="team1",
                         contact="product@owner.org")
        self.post_json("/products", prod_dict, status=201)

        status = self.delete('/products/' + product_name, status=204)
        self.assertEqual(204, status.status_int)

    def test_product_delete_as_user(self):
        product_name = 'test_product_delete_as_user'
        prod_dict = dict(name=product_name,
                         team="team1",
                         contact="product@owner.org")
        self.post_json("/products", prod_dict, status=201)

        status = self.delete('/products/' + product_name,
                             headers={'X-Auth-Token': utils.MEMBER_TOKEN},
                             expect_errors=True)
        self.assertEqual(403, status.status_int)
