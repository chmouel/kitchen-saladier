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

from sqlalchemy.orm import exc as orm_exc


class TestAPI(saladier.tests.db.BaseTestDb):
    def setUp(self):
        super(TestAPI, self).setUp()

    def test_create_product(self):
        self.db_api.create_product(self.session, name="name1", team="team1",
                                   contact="contact1")
        product = TestAPI.db_api.get_product_by_name(self.session, "name1")
        self.assertIsNotNone(product)
        self.assertEqual("name1", product["name"])
        self.assertEqual("team1", product["team"])
        self.assertEqual("contact1", product["contact"])

    def test_get_product_by_name(self):
        self.db_api.create_product(self.session, name="name1", team="team1",
                                   contact="contact1")
        self.db_api.create_product(self.session, name="name2", team="team2",
                                   contact="contact2")
        product1 = self.db_api.get_product_by_name(self.session, "name1")
        self.assertIsNotNone(product1)
        product2 = self.db_api.get_product_by_name(self.session, "name2")
        self.assertIsNotNone(product2)

    def test_get_all_products(self):
        self.db_api.create_product(self.session, name="name1", team="team1",
                                   contact="contact1")
        self.db_api.create_product(self.session, name="name2", team="team2",
                                   contact="contact2")
        all_products = self.db_api.get_all_products(self.session)
        self.assertEqual(len(all_products["products"]), 2)

    def test_update_product(self):
        self.db_api.create_product(self.session, name="name1", team="team1",
                                   contact="contact1")
        product = self.db_api.get_product_by_name(self.session, "name1")
        self.assertIsNotNone(product)
        self.assertEqual("name1", product["name"])
        self.assertEqual("team1", product["team"])
        self.assertEqual("contact1", product["contact"])

        self.db_api.update_product(self.session, "name1", "name2", "team2",
                                   "contact2")
        product = self.db_api.get_product_by_name(self.session, "name2")
        self.assertIsNotNone(product)
        self.assertEqual("name2", product["name"])
        self.assertEqual("team2", product["team"])
        self.assertEqual("contact2", product["contact"])

    def test_delete_product(self):
        self.db_api.create_product(self.session, name="name1", team="team1",
                                   contact="contact1")
        product = self.db_api.get_product_by_name(self.session, "name1")
        self.assertIsNotNone(product)
        self.db_api.delete_product(self.session, "name1")
        self.assertRaises(orm_exc.NoResultFound,
                          self.db_api.get_product_by_name,
                          self.session, "name1")

    def test_create_product_version(self):
        self.db_api.create_product(self.session, name="name1", team="team1",
                                   contact="contact1")
        self.db_api.create_product_version(self.session, "name1", "version1")

    def test_create_product_version_invalid_fk(self):
        self.db_api.create_product(self.session, name="name1", team="team1",
                                   contact="contact1")

        # TODO(yassine): self.assertRaises raises an exception which makes
        # the test to fail...
        raised = False
        try:
            self.db_api.create_product_version(self.session,
                                               "name2", "version1")
        except Exception:
            raised = True

        self.assertTrue(raised)

    def test_get_all_versions_of_product(self):
        self.db_api.create_product(self.session, name="name1", team="team1",
                                   contact="contact1")
        self.db_api.create_product_version(self.session, "name1", "version1")
        self.db_api.create_product_version(self.session, "name1", "version2")
        self.db_api.create_product_version(self.session, "name1", "version3")

        all_versions = self.db_api.get_all_versions_of_product(self.session,
                                                               "name1")
        self.assertIsNotNone(all_versions)
        self.assertEqual(3, len(all_versions))

    def test_create_customer(self):
        self.db_api.create_customer(self.session, name="customer1",
                                    contact="contact1")
        customer = self.db_api.get_customer_by_name(self.session, "customer1")
        self.assertIsNotNone(customer)

    def test_get_all_customers(self):
        self.db_api.create_customer(self.session, name="customer1",
                                    contact="contact1")
        self.db_api.create_customer(self.session, name="customer2",
                                    contact="contact2")
        self.db_api.create_customer(self.session, name="customer3",
                                    contact="contact3")

        all_customers = self.db_api.get_all_customers(self.session)
        self.assertIsNotNone(all_customers)
        self.assertEqual(len(all_customers["customers"]), 3)

    def test_create_platform(self):
        self.db_api.create_customer(self.session, name="customer1",
                                    contact="contact1")
        self.db_api.create_platform(self.session, name="platform1",
                                    location="location1",
                                    contact="contact1",
                                    customer_name="customer1")
        self.db_api.create_platform(self.session,
                                    name="platform2",
                                    location="location2",
                                    contact="contact2",
                                    customer_name="customer1")

        platforms = self.db_api.get_platforms_by_customer(
            self.session, customer_name="customer1")
        self.assertIsNotNone(platforms)
        self.assertEqual(2, len(platforms))

    def test_create_platform_invalid_fk(self):
        self.db_api.create_customer(self.session, name="customer1",
                                    contact="contact1")
        raised = False
        try:
            self.db_api.create_platform(self.session, location="location1",
                                        contact="contact1",
                                        customer_name="customer2")
        except Exception:
            raised = True

        self.assertTrue(raised)

    def test_get_all_platforms(self):
        self.db_api.create_customer(self.session, name="customer1",
                                    contact="contact1")
        self.db_api.create_customer(self.session, name="customer2",
                                    contact="contact2")
        self.db_api.create_platform(self.session,
                                    name='platform1',
                                    location="location1",
                                    contact="contact1",
                                    customer_name="customer1")
        self.db_api.create_platform(self.session,
                                    name='platorm2',
                                    location="location2",
                                    contact="contact2",
                                    customer_name="customer1")
        self.db_api.create_platform(self.session, location="location2",
                                    name='platform2',
                                    contact="contact2",
                                    customer_name="customer2")

        all_platforms = self.db_api.get_all_platforms(self.session)
        self.assertIsNotNone(all_platforms)
        self.assertEqual(3, len(all_platforms["platforms"]))
