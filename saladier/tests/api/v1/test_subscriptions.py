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
from saladier.tests.api import utils
import saladier.tests.api.v1.base as base


class TestSubscriptions(base.V1FunctionalTest):
    def test_subscriptions_create(self):
        product_name = "test_subscriptions_create"
        self._create_sample_product(name=product_name)

        subs_dict = dict(product_name=product_name,
                         tenant_id="0123456789")
        self.post_json("/subscriptions",
                       subs_dict,
                       status=201)

    def test_subscriptions_create_as_user_denied(self):
        product_name = "test_subscriptions_create_as_user_denied"
        self._create_sample_product(name=product_name)

        subs_dict = dict(product_name=product_name,
                         tenant_id="0123456789")
        self.post_json("/subscriptions",
                       subs_dict,
                       headers={'X-Auth-Token': utils.MEMBER_TOKEN},
                       status=403)

    def test_subscriptions_duplicate_error(self):
        product_name = "test_subscriptions_duplicate_error"
        self._create_sample_product(name=product_name)

        subs_dict = dict(product_name=product_name,
                         tenant_id="0123456789")

        self.post_json("/subscriptions", subs_dict, status=201)
        self.post_json("/subscriptions", subs_dict, status=409)

    def test_subscriptions_delete(self):
        product_name = "test_subscriptions_delete"
        tenant_id = "0123456789"

        self._create_sample_product(name=product_name)

        subs_dict = dict(product_name=product_name,
                         tenant_id=tenant_id)
        self.post_json("/subscriptions",
                       subs_dict,
                       status=201)

        self.delete("/subscriptions/%s/%s/" % (product_name, tenant_id),
                    status=204)

    def test_subscriptions_delete_as_user_denied(self):
        product_name = "test_subscriptions_delete_as_user_denied"
        tenant_id = "0123456789"

        self._create_sample_product(name=product_name)

        subs_dict = dict(product_name=product_name,
                         tenant_id=tenant_id)
        self.post_json("/subscriptions",
                       subs_dict,
                       status=201)

        self.delete("/subscriptions/%s/%s/" % (product_name, tenant_id),
                    headers={'X-Auth-Token': utils.MEMBER_TOKEN},
                    status=403)

    def test_subscriptions_list(self):
        product_name = "test_subscriptions_list"
        tenant_id = "0123456789"

        self._create_sample_product(name=product_name)

        subs_dict = dict(product_name=product_name,
                         tenant_id=tenant_id)
        self.post_json("/subscriptions",
                       subs_dict,
                       status=201)

        ret = self.get_json("/subscriptions/%s" % (tenant_id), status=200)
        self.assertEqual(tenant_id, ret['subscriptions'][0]['tenant_id'])

    def test_subscriptions_list_user_denied(self):
        # FIXME(chmou): we have this but in the future this should be allowed
        # tailored to the user view permissions.
        product_name = "test_subscriptions_list_user_denied"
        tenant_id = "0123456789"

        self._create_sample_product(name=product_name)

        subs_dict = dict(product_name=product_name,
                         tenant_id=tenant_id)
        self.post_json("/subscriptions",
                       subs_dict,
                       status=201)

        self.get_json("/subscriptions/%s" % (tenant_id),
                      headers={'X-Auth-Token': utils.MEMBER_TOKEN},
                      status=403)

    def test_product_list_only_for_certain_tenant(self):
        product_name = 'test_product_list_only_for_certain_tenant'
        version = '1.0'
        tenant_id_owner = utils.MEMBER_TENANT_ID

        self._create_sample_product(name=product_name)

        self._create_sample_product_version(product=product_name,
                                            version=version)

        subs_dict = dict(product_name=product_name,
                         tenant_id=tenant_id_owner)
        self.post_json("/subscriptions", subs_dict, status=201)

        data = self.get_json('/products/',
                             headers={'X-Auth-Token':
                                      utils.MEMBER_OTHER_TOKEN})
        self.assertNotIn(product_name, data['products'])

    def test_product_directly_owner(self):
        product_name = 'test_product_directly_owner'
        version = '1.0'
        tenant_id_owner = utils.MEMBER_TENANT_ID

        self._create_sample_product(name=product_name)
        self._create_sample_product_version(product=product_name,
                                            version=version)

        subs_dict = dict(product_name=product_name,
                         tenant_id=tenant_id_owner)
        self.post_json("/subscriptions", subs_dict, status=201)

        # NOTE(chmou): 404 error cause it's not accessible to
        # MEMBER_OTHER_TOKEN
        data = self.get_json('/products/%s' % (product_name),
                             headers={'X-Auth-Token': utils.MEMBER_TOKEN},
                             status=200)
        self.assertIn("1.0", data['versions'])

    def test_product_directly_not_owner(self):
        product_name = 'test_product_directly_not_owner'
        version = '1.0'
        tenant_id_owner = utils.MEMBER_TENANT_ID

        self._create_sample_product(name=product_name)
        self._create_sample_product_version(product=product_name,
                                            version=version)

        subs_dict = dict(product_name=product_name,
                         tenant_id=tenant_id_owner)
        self.post_json("/subscriptions", subs_dict, status=201)

        # NOTE(chmou): 404 error cause it's not accessible to
        # MEMBER_OTHER_TOKEN
        self.get_json('/products/%s' % (product_name),
                      headers={'X-Auth-Token':
                               utils.MEMBER_OTHER_TOKEN}, status=404)

    def test_product_version_directly_not_owner(self):
        product_name = 'test_product_version_directly_not_owner'
        version = '1.0'
        tenant_id_owner = utils.MEMBER_TENANT_ID

        self._create_sample_product(name=product_name)
        self._create_sample_product_version(product=product_name,
                                            version=version)

        subs_dict = dict(product_name=product_name,
                         tenant_id=tenant_id_owner)
        self.post_json("/subscriptions", subs_dict, status=201)

        # NOTE(chmou): 404 error cause it's not accessible to
        # MEMBER_OTHER_TOKEN
        self.get_json('/products/%s/%s' % (product_name, version),
                      headers={'X-Auth-Token':
                               utils.MEMBER_OTHER_TOKEN}, status=404)
