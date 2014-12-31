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


class ProductVersionTestCase(base.DbTestCase):
    def test_create_product_version(self):
        product = self.dbapi.create_product(
            name="product1", team="team1", contact="contact1")
        for version in ["1.0", "1.1"]:
            self.dbapi.create_product_version(product.id,
                                              version=version,
                                              url="http://localhost/")

        all_versions = [d.version for d in
                        self.dbapi.get_all_product_versions(product.id)]
        self.assertIn("1.0", all_versions)

    def test_create_product_version_already_exists(self):
        product = self.dbapi.create_product(
            name="product1", team="team1", contact="contact1")
        self.dbapi.create_product_version(product.id,
                                          "1.0",
                                          url="http://localhost/")
        self.assertRaises(exception.ProductVersionAlreadyExists,
                          self.dbapi.create_product_version,
                          product.id,
                          "1.0",
                          "http://localhost/")

    def test_delete_product_version(self):
        product = self.dbapi.create_product(
            name="product1", team="team1", contact="contact1")
        self.dbapi.create_product_version(product.id,
                                          "1.0",
                                          url="http://localhost/")
        self.dbapi.delete_product_versions(product.id,
                                           "1.0")

        self.assertEqual([],
                         self.dbapi.get_all_product_versions(product.id))

    def test_create_product_version_missing(self):
        self.assertRaises(exception.ProductVersionNotFound,
                          self.dbapi.get_product_version_by_id,
                          69)
