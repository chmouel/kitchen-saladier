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


class ProductTestCase(base.DbTestCase):
    def test_create_product(self):
        self.dbapi.create_product(name="name1", team="team1",
                                  contact="contact1")
        product = self.dbapi.get_product("name1", tenant_id='', admin=True)
        self.assertEqual("name1", product["name"])
        self.assertEqual("team1", product["team"])
        self.assertEqual("contact1", product["contact"])

    def test_get_product(self):
        self.dbapi.create_product(name="name1", team="team1",
                                  contact="contact1")
        product_v1 = self.dbapi.get_product(
            "name1", tenant_id='', admin=True)
        product_v2 = self.dbapi.get_product(
            product_v1.id, tenant_id='', admin=True)
        self.assertEqual(product_v1.id, product_v2.id)

    def test_delete_product(self):
        self.dbapi.create_product(name="name1", team="team1",
                                  contact="contact1")
        self.dbapi.delete_product("name1")
        self.assertRaises(exception.ProductNotFound,
                          self.dbapi.get_product,
                          "fake_uuid", tenant_id='', admin=True)

    def test_get_product_notfound(self):
        self.assertRaises(exception.ProductNotFound,
                          self.dbapi.get_product,
                          "fake_uuid", tenant_id='', admin=True)

    def test_create_product_conflict(self):
        self.dbapi.create_product(name="name1", team="team1",
                                  contact="contact1")
        self.assertRaises(exception.ProductAlreadyExists,
                          self.dbapi.create_product, name="name1",
                          team="team1",
                          contact="contact1")
