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


SAMPLE_JSON_PRODUCTS_NAME = {'contact': 'product@owner.org',
                             'team': 'team1',
                             'versions': {'1.0': {'ready_for_deploy': False,
                                                  'validated_on': {}},
                                          '1.1': {'ready_for_deploy': False,
                                                  'validated_on': {}}}}

SAMPLE_JSON_PRODUCTS = {'products':
                        {'name1': ['1.0', '1.1'],
                         'name2': ['2.0', '2.1']}}


class TestProducts(base.FunctionalTest):
    def setUp(self):
        super(TestProducts, self).setUp()

    def _create_sample_product(self, name=None,
                               team=None,
                               contact=None):
        name = name or 'name1'
        team = team or SAMPLE_JSON_PRODUCTS_NAME['team']
        contact = contact or SAMPLE_JSON_PRODUCTS_NAME['contact']
        prod_dict = dict(name=name,
                         team=team,
                         contact=contact)
        self.post_json("/products", prod_dict, status=201)

    def _create_sample_product_version(self, product=None, url=None,
                                       version=None):
        product = product or 'name1'
        url = url or 'http://sample_url'
        version = version or ''

        version_dict = dict(product=product, url=url, version=version)
        self.post_json("/versions", version_dict, status=201)

    def test_product_version_create_list(self):
        self._create_sample_product(name='name1')
        self._create_sample_product(name='name2')

        for version in SAMPLE_JSON_PRODUCTS['products']['name1']:
            self._create_sample_product_version(product='name1',
                                                version=version)
        for version in SAMPLE_JSON_PRODUCTS['products']['name2']:
            self._create_sample_product_version(product='name2',
                                                version=version)

        self.assertEqual(SAMPLE_JSON_PRODUCTS, self.get_json('/products/'))

    def test_product_get_by_name_has_versions(self):
        name = 'name1'
        self._create_sample_product(name=name)

        for version in SAMPLE_JSON_PRODUCTS['products'][name]:
            self._create_sample_product_version(product=name,
                                                version=version)

        self.assertEqual(SAMPLE_JSON_PRODUCTS_NAME,
                         self.get_json('/products/' + name))

    def test_product_get_by_name_no_version(self):
        name = 'name1'
        self._create_sample_product(name=name)

        ret_dict = {'versions': {},
                    'contact': SAMPLE_JSON_PRODUCTS_NAME['contact'],
                    'team': SAMPLE_JSON_PRODUCTS_NAME['team']}
        self.assertEqual(ret_dict, self.get_json('/products/' + name))

    def test_product_get_by_name_and_version(self):
        name = 'name1'
        version = '1.0'

        self._create_sample_product(name=name)
        for version in SAMPLE_JSON_PRODUCTS['products'][name]:
            self._create_sample_product_version(product=name,
                                                version=version)

        ret_dict = SAMPLE_JSON_PRODUCTS_NAME['versions'][version]
        self.assertEqual(ret_dict,
                         self.get_json('/products/%s/%s' %
                                       (name, version)))

    def test_product_create_conflict(self):
        prod_dict = dict(name="name1",
                         team="team1",
                         contact="product@owner.org")
        self.post_json("/products", prod_dict, status=201)

        prod_dict = dict(name="name1",
                         team="team1",
                         contact="product@owner.org")
        ret = self.post_json("/products", prod_dict, status=409)
        self.assertEqual(409, ret.status_int)

    def test_product_create_notfound(self):
        self.get_json('/products/random', status=404)

    def test_product_delete(self):
        prod_dict = dict(name="name1",
                         team="team1",
                         contact="product@owner.org")
        self.post_json("/products", prod_dict, status=201)

        status = self.delete('/products/name1', status=204)
        self.assertEqual(204, status.status_int)

    def test_product_delete_as_user(self):
        prod_dict = dict(name="name1",
                         team="team1",
                         contact="product@owner.org")
        self.post_json("/products", prod_dict, status=201)

        status = self.delete('/products/name1',
                             headers={'X-Auth-Token': utils.MEMBER_TOKEN},
                             expect_errors=True)
        self.assertEqual(403, status.status_int)
