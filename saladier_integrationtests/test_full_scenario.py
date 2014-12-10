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
import saladier_integrationtests.common.base as base


class TestFullScenario(base.Base):
    def test_discover_version(self):
        version = self.user_client.server_info.list()
        self.assertEqual('Paris', version.location)

    def test_create_product_version(self):
        # NOTE(chmou): where the f*** in a name why I have chosen tenant_id
        # instead of tenant_name
        user_tenant_id = (self.user_client.http_client.auth_ref['token']
                          ['tenant']['id'])

        # product_create
        product_dict = dict(team="boa",
                            name="product1",
                            contact="cedric@isthegreatest.com")
        self.admin_client.products.create(**product_dict)

        # product_get (admin)
        product_admin_resp = self.admin_client.products.get(
            product_dict['name'])
        self.assertDictContainsSubset(dict(team=product_dict['team'],
                                           contact=product_dict['contact']),
                                      product_admin_resp.to_dict())
        product_id = product_admin_resp.id

        # product_version_create
        product_version_dict = dict(product_id=product_id,
                                    url='http://blah.com',
                                    version='1.0')
        self.admin_client.product_versions.create(**product_version_dict)

        # Create platform
        platform_dict = dict(name="platform1",
                             location="ParisEstMagique",
                             contact="thecedric@isthegreatest.com",
                             tenant_id=user_tenant_id)
        self.admin_client.platforms.create(**platform_dict)

        # platform_list
        platforms_resp = self.user_client.platforms.list()
        self.assertDictContainsSubset(
            platform_dict, platforms_resp[0].to_dict())

        # product_subscription_create
        subscription_dict = dict(product_id=product_id,
                                 tenant_id=user_tenant_id)
        self.admin_client.subscriptions.create(**subscription_dict)

        # product_list
        products_resp = self.user_client.products.list()
        # NOTE(chmou): until http://is.gd/VnO3lx is fixed
        pdtemp = product_dict.copy()
        del pdtemp['name']
        self.assertDictContainsSubset(pdtemp,
                                      products_resp[0].to_dict())

        # product_get
        products_resp = self.user_client.products.get(
            product_dict['name'])
        self.assertDictContainsSubset(pdtemp,
                                      products_resp.to_dict())
        self.assertEqual(
            products_resp.to_dict()['versions'][0]['version'],
            product_version_dict['version'])
        version_id = products_resp.to_dict()['versions'][0]['id']

        # product_get_version
        products_resp = self.user_client.products.get(
            product_dict['name'],
            version=version_id)

        version_dict = dict(
            id=version_id, version=product_version_dict['version'],
            ready_for_deploy=False, validated_on=[])
        self.assertDictEqual(version_dict, products_resp.to_dict())

        # product_version_status_add
        platform_id = platforms_resp[0].id
        product_version_id = products_resp.id
        status_dict = {
            'platform_id': platform_id,
            'product_version_id': product_version_id,
            'status': 'NOT_TESTED',
            'logs_location': 'A_galaxy-far-far-away'
        }
        self.admin_client.status.create(**status_dict)

        # product_version_status_get
        status_resp = self.user_client.status.get(platform_id,
                                                  product_version_id)
        self.assertDictContainsSubset(status_dict, status_resp.to_dict())

        # product_version_status_update
        new_status_dict = status_dict.copy()
        new_status_dict['status'] = 'CREATED'
        self.user_client.status.update(new_status_dict)

        new_status_resp = self.user_client.status.get(platform_id,
                                                      product_version_id)
        self.assertEqual(new_status_dict['status'],
                         new_status_resp.status)
