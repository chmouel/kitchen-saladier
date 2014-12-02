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
from saladier.db.sqlalchemy import models
from saladier.tests.api import utils
import saladier.tests.api.v1.base as base


class TestProducts(base.V1FunctionalTest):
    def setUp(self):
        super(TestProducts, self).setUp()

    def test_product_version_create_list(self):
        product_id1 = self._create_sample_product(name='name1')
        product_id2 = self._create_sample_product(name='name2')

        for version in base.SAMPLE_JSON_PRODUCTS_INPUT['products']['name1']:
            self._create_sample_product_version(product_id=product_id1,
                                                version=version)
        for version in base.SAMPLE_JSON_PRODUCTS_INPUT['products']['name2']:
            self._create_sample_product_version(product_id=product_id2,
                                                version=version)
        result = self.get_json('/products/')
        # NOTE(Gonéri): Removing auto generated results from the return
        for product in result['products']:
            product['id'] = 'skip'
            for version in product['versions']:
                version['id'] = 'skip'
                version['version'] = 'skip'
        self.assertEqual(base.SAMPLE_JSON_PRODUCTS_EXPECT,
                         result)

    def test_product_get_by_name_has_versions(self):
        product_id = self._create_sample_product(name='name1')

        self._create_sample_product_version(
            product_id=product_id,
            version="1.0")
        self._create_sample_product_version(
            product_id=product_id,
            version="1.1")
        result = self.get_json('/products/' + product_id)
        self.assertEqual(2, len(result["versions"]))
        # TODO(Gonéri): we should use an order_by to ensure we keep the
        # order
        self.assertEqual(["1.0", "1.1"], sorted([x['version']
                                                 for x in result['versions']]))

    def test_product_get_by_name_no_version(self):
        product_id = self._create_sample_product(name='name1')

        ret_dict = {'id': product_id,
                    'versions': [],
                    'contact': base.SAMPLE_JSON_PRODUCTS_NAME['contact'],
                    'team': base.SAMPLE_JSON_PRODUCTS_NAME['team']}
        self.assertEqual(ret_dict, self.get_json('/products/%s' % product_id))

    def test_product_get_by_name_and_version(self):
        version = '1.0'

        product_id = self._create_sample_product(name='name1')
        for version in base.SAMPLE_JSON_PRODUCTS_INPUT['products']['name1']:
            product_version_id = self._create_sample_product_version(
                product_id=product_id,
                version=version)

        ret_dict = base.SAMPLE_JSON_PRODUCTS_NAME['versions'][version]
        result = self.get_json('/products/%s/%s' % (product_id,
                                                    product_version_id))
        self.assertEqual(ret_dict['ready_for_deploy'],
                         result['ready_for_deploy'])
        self.assertEqual(ret_dict['validated_on'], result['validated_on'])

    def test_product_get_by_name_bad_version(self):
        product_id = self._create_sample_product(name='name1')
        self.get_json(
            "/products/%s/bad_version" % product_id,
            status=404)

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

    def test_product_with_version_status(self):
        product_id = self._create_sample_product(name='name1')
        self._create_sample_product_version(
            product_id=product_id, version="1.0")
        pv_id = self._get_product_version_id_by_version_name(product_id, "1.0")
        platform_id = self._create_sample_platform(
            name='plat1', location='location1', contact='contact1')

        status_dict = dict(platform_id=platform_id,
                           product_version_id=pv_id,
                           status=models.Status.NOT_TESTED,
                           logs_location="swift://localhost/deploy")
        self.post_json("/status", status_dict, status=201)
        result = self.get_json('/products/%s/%s' % (product_id, pv_id))
        self.assertEqual(1, len(result['validated_on']))
        result_validated_on = result['validated_on'][0]
        self.assertEqual(platform_id, result_validated_on['platform_id'])
        self.assertEqual('swift://localhost/deploy',
                         result_validated_on['logs_location'])
        self.assertEqual('NOT_TESTED', result_validated_on['status'])

    def test_product_with_update_version_status(self):
        product_id = self._create_sample_product(name='name1')
        pv_id = self._create_sample_product_version(
            product_id=product_id, version="1.0")
        platform_id = self._create_sample_platform(
            name='plat1', location='location1', contact='contact1')

        status_dict = dict(platform_id=platform_id,
                           product_version_id=pv_id,
                           status=models.Status.NOT_TESTED,
                           logs_location="swift://localhost/deploy")
        self.post_json("/status", status_dict, status=201)

        new_status_dict = dict(platform_id=platform_id,
                               product_version_id=pv_id,
                               status=models.Status.SUCCESS,
                               logs_location="swift://localhost/deploy")
        self.put_json("/status", new_status_dict, status=204)
        result = self.get_json('/products/%s/%s' % (product_id, pv_id))
        result_validated_on = result['validated_on'][0]
        self.assertEqual('SUCCESS', result_validated_on['status'])
