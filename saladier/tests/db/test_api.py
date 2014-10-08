# -*- coding: utf-8 -*-
#
# Copyright 2014 eNovance SAS <licensing@enovance.com>
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

import saladier.tests.db

from sqlalchemy.orm import exc


class TestAPI(saladier.tests.db.BaseTestDb):
    def setUp(self):
        super(TestAPI, self).setUp()

    def test_create_product(self):
        self.db_api.create_product(self.session, name="name1", team="team1",
                                   contact="contact1")
        product = TestAPI.db_api.get_product_by_name(self.session, "name1")
        self.assertIsNotNone(product)
        self.assertEqual("name1", product.name)
        self.assertEqual("team1", product.team)
        self.assertEqual("contact1", product.contact)

    def test_get_product_by_name(self):
        self.db_api.create_product(self.session, name="name1", team="team1",
                                   contact="contact1")
        self.db_api.create_product(self.session, name="name2", team="team2",
                                   contact="contact2")
        product1 = self.db_api.get_product_by_name(self.session, "name1")
        self.assertIsNotNone(product1)
        product2 = self.db_api.get_product_by_name(self.session, "name2")
        self.assertIsNotNone(product2)

    def test_get_products(self):
        self.db_api.create_product(self.session, name="name1", team="team1",
                                   contact="contact1")
        self.db_api.create_product(self.session, name="name2", team="team2",
                                   contact="contact2")
        products = self.db_api.get_products(self.session)
        self.assertEqual(len(products["products"]), 2)

    def test_update_product(self):
        self.db_api.create_product(self.session, name="name1", team="team1",
                                   contact="contact1")
        product = self.db_api.get_product_by_name(self.session, "name1")
        self.assertIsNotNone(product)
        self.assertEqual("name1", product.name)
        self.assertEqual("team1", product.team)
        self.assertEqual("contact1", product.contact)

        self.db_api.update_product(self.session, "name1", "name2", "team2",
                                   "contact2")
        product = self.db_api.get_product_by_name(self.session, "name2")
        self.assertIsNotNone(product)
        self.assertEqual("name2", product.name)
        self.assertEqual("team2", product.team)
        self.assertEqual("contact2", product.contact)

    def test_delete_product(self):
        self.db_api.create_product(self.session, name="name1", team="team1",
                                   contact="contact1")
        product = self.db_api.get_product_by_name(self.session, "name1")
        self.assertIsNotNone(product)
        self.db_api.delete_product(self.session, "name1")
        self.assertRaises(exc.NoResultFound, self.db_api.get_product_by_name,
                          self.session, "name1")
