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
import saladier.common.exception as exception
import saladier.tests.db.base as base


class SubscriptionTestCase(base.DbTestCase):
    def test_list_subscription_by_tenant_id(self):
        product_name = "name1"
        tenant_id = '0123456789'

        product = self.dbapi.create_product(
            name=product_name, team="team1", contact="contact1")
        self.dbapi.create_subscription(tenant_id=tenant_id,
                                       product_id=product.id)

        all_sub = [x.product_id
                   for x in
                   self.dbapi.get_subscriptions_for_tenant_id(tenant_id)]
        self.assertIn(product.id, all_sub)

    def test_list_subscription_by_tenant_id_default_empty(self):
        tenant_id = '0123456789'

        self.dbapi.create_product(name="name1", team="team1",
                                  contact="contact1")

        self.assertEqual([],
                         self.dbapi.get_subscriptions_for_tenant_id(tenant_id))

    def test_not_listing_subscription_from_other_tenant_id(self):
        tenant_id = '0123456789'
        other_tenant_id = '222222222'

        product = self.dbapi.create_product(
            name="name1", team="team1", contact="contact1")
        self.dbapi.create_subscription(tenant_id=tenant_id,
                                       product_id=product.id)

        all_sub = [x.product_name
                   for x in
                   self.dbapi.get_subscriptions_for_tenant_id(other_tenant_id)]
        self.assertEqual([], all_sub)

    def test_subscription_duplicate_error(self):
        tenant_id = '0123456789'

        product = self.dbapi.create_product(
            name="name1", team="team1", contact="contact1")
        self.dbapi.create_subscription(tenant_id=tenant_id,
                                       product_id=product.id)

        self.assertRaises(
            exception.SubscriptionAlreadyExists,
            self.dbapi.create_subscription,
            tenant_id=tenant_id,
            product_id=product.id)

    def test_delete_subscription(self):
        tenant_id = '0123456789'

        product = self.dbapi.create_product(
            name="name1", team="team1", contact="contact1")
        self.dbapi.create_subscription(tenant_id=tenant_id,
                                       product_id=product.id)

        all_sub = [x.product_id
                   for x in
                   self.dbapi.get_subscriptions_for_tenant_id(tenant_id)]
        self.assertIn(product.id, all_sub)

        self.dbapi.delete_subscription(tenant_id=tenant_id,
                                       product_id=product.id)
        all_sub = [x.product_name
                   for x in
                   self.dbapi.get_subscriptions_for_tenant_id(tenant_id)]
        self.assertEqual([], all_sub)

    def test_subscriptions_list_own(self):
        tenant_id = '0123456789'

        product = self.dbapi.create_product(
            name="name1", team="team1", contact="contact1")
        self.dbapi.create_subscription(tenant_id=tenant_id,
                                       product_id=product.id)

        all_sub = [x.id for x in self.dbapi.get_all_products(
            tenant_id=tenant_id)]
        self.assertEqual([product.id], all_sub)

    def test_subscriptions_list_all_admin(self):
        tenant_id = '0123456789'
        tenant_id_other = '1111111111'

        product = self.dbapi.create_product(
            name="name1", team="team1", contact="contact1")
        self.dbapi.create_subscription(tenant_id=tenant_id,
                                       product_id=product.id)

        all_sub = [x.id for x in self.dbapi.get_all_products(
            tenant_id=tenant_id_other, admin=True)]
        self.assertEqual([product.id], all_sub)

    def test_subscriptions_list_not_showing_other_tenant(self):
        tenant_id = '0123456789'
        tenant_id_other = '1111111111'

        product = self.dbapi.create_product(
            name="name1", team="team1", contact="contact1")
        self.dbapi.create_subscription(tenant_id=tenant_id,
                                       product_id=product.id)

        all_sub = [x.name for x in self.dbapi.get_all_products(
            tenant_id=tenant_id_other)]
        self.assertEqual([], all_sub)
