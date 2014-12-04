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
        self._create_sample_product(name='name1')
        self._create_sample_product(name='name2')

        for version in base.SAMPLE_JSON_PRODUCTS['products']['name1']:
            self._create_sample_product_version(product='name1',
                                                version=version)
        for version in base.SAMPLE_JSON_PRODUCTS['products']['name2']:
            self._create_sample_product_version(product='name2',
                                                version=version)
        result = self.get_json('/products/')

        for p in base.SAMPLE_JSON_PRODUCTS["products"]:
            base.SAMPLE_JSON_PRODUCTS["products"][p].sort()
            result['products'][p].sort()

        self.assertEqual(base.SAMPLE_JSON_PRODUCTS,
                         result)

    def test_product_get_by_name_has_versions(self):
        name = 'name1'
        self._create_sample_product(name=name)

        for version in base.SAMPLE_JSON_PRODUCTS['products'][name]:
            self._create_sample_product_version(product=name,
                                                version=version)
        result = self.get_json('/products/' + name)
        self.assertEqual(2, len(result["versions"]))
        self.assertIn("1.0", result["versions"])
        self.assertIn("1.1", result["versions"])

    def test_product_get_by_name_no_version(self):
        name = 'name1'
        self._create_sample_product(name=name)

        ret_dict = {'versions': {},
                    'contact': base.SAMPLE_JSON_PRODUCTS_NAME['contact'],
                    'team': base.SAMPLE_JSON_PRODUCTS_NAME['team']}
        self.assertEqual(ret_dict, self.get_json('/products/' + name))

    def test_product_get_by_name_and_version(self):
        name = 'name1'
        version = '1.0'

        self._create_sample_product(name=name)
        for version in base.SAMPLE_JSON_PRODUCTS['products'][name]:
            self._create_sample_product_version(product=name,
                                                version=version)

        ret_dict = base.SAMPLE_JSON_PRODUCTS_NAME['versions'][version]
        result = self.get_json('/products/%s/%s' % (name, version))
        self.assertEqual(ret_dict['ready_for_deploy'],
                         result['ready_for_deploy'])
        self.assertEqual(ret_dict['validated_on'], result['validated_on'])

    def test_product_get_by_name_and_non_existing_version(self):
        name = 'name1'
        version = 'None'

        self._create_sample_product(name=name)
        self.get_json('/products/%s/%s' % (name, version), status=404)

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
        self._create_sample_product(name='name1')
        self._create_sample_product_version(product='name1', version="1.0")
        pv_id = self._get_product_version_id("name1", "1.0")
        self._create_sample_platform(name='plat1', location='location1',
                                     contact='contact1')

        status_dict = dict(platform_name='plat1',
                           product_version_id=pv_id,
                           status=models.Status.NOT_TESTED,
                           logs_location="swift://localhost/deploy")
        self.post_json("/status", status_dict, status=201)
        result = self.get_json('/products/name1/1.0')
        self.assertEqual(1, len(result['validated_on']))
        result_validated_on = result['validated_on'][0]
        self.assertEqual('plat1', result_validated_on['platform_name'])
        self.assertEqual('swift://localhost/deploy',
                         result_validated_on['logs_location'])
        self.assertEqual('NOT_TESTED', result_validated_on['status'])

    def test_product_with_update_version_status(self):
        self._create_sample_product(name='name1')
        self._create_sample_product_version(product='name1', version="1.0")
        pv_id = self._get_product_version_id("name1", "1.0")
        self._create_sample_platform(name='plat1', location='location1',
                                     contact='contact1')

        status_dict = dict(platform_name='plat1',
                           product_version_id=pv_id,
                           status=models.Status.NOT_TESTED,
                           logs_location="swift://localhost/deploy")
        self.post_json("/status", status_dict, status=201)

        new_status_dict = dict(platform_name='plat1',
                               product_version_id=pv_id,
                               new_status=models.Status.SUCCESS,
                               new_logs_location="swift://localhost/deploy")
        self.put_json("/status", new_status_dict, status=204)
        result = self.get_json('/products/name1/1.0')
        result_validated_on = result['validated_on'][0]
        self.assertEqual('SUCCESS', result_validated_on['status'])