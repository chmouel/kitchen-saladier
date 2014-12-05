# -*- coding: utf-8 -*-
# Copyright (C) 2014 eNovance SAS <licensing@enovance.com>
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.
import saladier.tests.api.base as base

SAMPLE_JSON_PRODUCTS_NAME = {'contact': 'product@owner.org',
                             'team': 'team1',
                             'versions': {'1.0': {'ready_for_deploy': False,
                                                  'validated_on': []},
                                          '1.1': {'ready_for_deploy': False,
                                                  'validated_on': {}}}}
SAMPLE_JSON_PRODUCTS_INPUT = {'products': {'name1': ['1.1', '1.0'],
                                           'name2': ['2.0', '2.1']}}
SAMPLE_JSON_PRODUCTS_EXPECT = {
    'products': [
        {
            'contact': 'product@owner.org',
            'id': 'skip',
            'team': 'team1',
            'name': 'product1',
            'versions': [{'id': 'skip',
                          'ready_for_deploy': False,
                          'validated_on': [],
                          'version': 'skip'},
                         {'id': 'skip',
                          'ready_for_deploy': False,
                          'validated_on': [],
                          'version': 'skip'},
                         {'id': 'skip',
                          'ready_for_deploy': False,
                          'validated_on': [],
                          'version': 'skip'},
                         {'id': 'skip',
                          'ready_for_deploy': False,
                          'validated_on': [],
                          'version': 'skip'}]},
        {
            'contact': 'product@owner.org',
            'id': 'skip',
            'team': 'team1',
            'name': 'product2',
            'versions': [{'id': 'skip',
                          'ready_for_deploy': False,
                          'validated_on': [],
                          'version': 'skip'},
                         {'id': 'skip',
                          'ready_for_deploy': False,
                          'validated_on': [],
                          'version': 'skip'},
                         {'id': 'skip',
                          'ready_for_deploy': False,
                          'validated_on': [],
                          'version': 'skip'},
                         {'id': 'skip',
                          'ready_for_deploy': False,
                          'validated_on': [],
                          'version': 'skip'}]
        }
    ]
}
SAMPLE_JSON_PLATFORM = {'contact': 'platform@owner.org',
                        'location': 'Paris',
                        'name': 'platform1',
                        'tenant_id': '87db9196-7483-11e4-9d91-0021ccd9d101'}


class V1FunctionalTest(base.FunctionalTest):
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
        return self._get_product_id(name)

    def _create_sample_product_version(self, product_id=None,
                                       url=None, version=None):
        url = url or 'http://sample_url'
        version = version or ''

        version_dict = dict(product_id=product_id, url=url, version=version)
        self.post_json("/versions", version_dict, status=201)
        return self._get_product_version_id_by_version_name(product_id,
                                                            version)

    def _get_product_version_id_by_version_name(self, product_id, version):
        data = self.get_json('/products/%s' % (product_id))
        for v in data['versions']:
            if v['version'] == version:
                return(v['id'])

    def _get_product_id(self, product_name):
        data = self.get_json('/products/%s' % product_name)
        return data['id']

    def _get_platform_id(self, platform_name):
        data = self.get_json('/platforms/%s' % platform_name)
        return data['id']

    def _create_sample_platform(self, name=None, location=None, contact=None,
                                tenant_id=None):
        name = name or SAMPLE_JSON_PLATFORM['name']
        location = location or SAMPLE_JSON_PLATFORM['location']
        contact = contact or SAMPLE_JSON_PLATFORM['contact']
        tenant_id = tenant_id or SAMPLE_JSON_PLATFORM['tenant_id']
        plat_dict = dict(name=name,
                         location=location,
                         contact=contact,
                         tenant_id=tenant_id)
        self.post_json("/platforms", plat_dict, status=201)
        return self._get_platform_id(name)

    def _add_version_status(self, platform_id, product_version_id, status,
                            logs_location):
        status_dict = dict(platform=platform_id,
                           product_version_id=product_version_id,
                           status=status,
                           logs_location=logs_location)
        self.post_json("/status", status_dict, status=201)
