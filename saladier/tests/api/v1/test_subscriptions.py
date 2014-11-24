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
        product_name = "name1"
        self._create_sample_product(name=product_name)

        subs_dict = dict(product_name=product_name,
                         tenant_id="0123456789")
        self.post_json("/subscriptions",
                       subs_dict,
                       status=201)

    def test_subscriptions_create_as_user_denied(self):
        product_name = "name1"
        self._create_sample_product(name=product_name)

        subs_dict = dict(product_name=product_name,
                         tenant_id="0123456789")
        self.post_json("/subscriptions",
                       subs_dict,
                       headers={'X-Auth-Token': utils.MEMBER_TOKEN},
                       status=403)

    def test_subscriptions_duplicate_error(self):
        product_name = "name1"
        self._create_sample_product(name=product_name)

        subs_dict = dict(product_name=product_name,
                         tenant_id="0123456789")

        self.post_json("/subscriptions", subs_dict, status=201)
        self.post_json("/subscriptions", subs_dict, status=409)

    def test_subscriptions_delete(self):
        product_name = "name1"
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
        product_name = "name1"
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
        product_name = "name1"
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
        product_name = "name1"
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
