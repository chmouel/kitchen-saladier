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
from saladier.common import exception
from saladier.db.sqlalchemy import models
import saladier.tests.db.base as base


class ProductVersionStatusTestCase(base.DbTestCase):

    version_status_deps = {"prod_name": "product1", "team": "team1",
                           "prod_contact": "contact1", "version": "1.0",
                           "uri": "http://localhost/", "plat_name": "name1",
                           "location": "location1", "plat_contact": "contact1",
                           "tenant_id": "tenant1"}

    def _create_product_version_status_deps(self, prod_name, team,
                                            prod_contact, version, uri,
                                            plat_name, location, plat_contact,
                                            tenant_id):
        self.dbapi.create_product(name=prod_name, team=team,
                                  contact=prod_contact)
        self.dbapi.create_product_version(prod_name, version=version,
                                          uri=uri)
        self.dbapi.create_platform(name=plat_name, location=location,
                                   contact=plat_contact, tenant_id=tenant_id)

    def test_add_product_status(self):
        self._create_product_version_status_deps(**self.version_status_deps)
        product_version_id = self.dbapi.get_all_product_versions(
            product_name="product1")[0].id

        all_product_status = self.dbapi.get_all_versions_status()
        self.assertEqual(0, len(all_product_status))

        self.dbapi.add_version_status("name1", product_version_id,
                                      models.Status.NOT_TESTED,
                                      "swift://localhost/deployment")
        all_product_status = self.dbapi.get_all_versions_status()
        self.assertEqual(1, len(all_product_status))

    def test_add_existing_product_status(self):
        self._create_product_version_status_deps(**self.version_status_deps)
        product_version_id = self.dbapi.get_all_product_versions(
            product_name="product1")[0].id
        self.dbapi.add_version_status("name1", product_version_id,
                                      models.Status.NOT_TESTED,
                                      "swift://localhost/deployment")
        self.assertRaises(exception.ProductVersionStatusAlreadyExists,
                          self.dbapi.add_version_status, "name1",
                          product_version_id, models.Status.NOT_TESTED,
                          "swift://localhost/deployment")

    def test_get_version_status(self):
        self._create_product_version_status_deps(**self.version_status_deps)
        product_version_id = self.dbapi.get_all_product_versions(
            product_name="product1")[0].id
        self.dbapi.add_version_status("name1", product_version_id,
                                      models.Status.NOT_TESTED,
                                      "swift://localhost/deployment")
        created_version_status = self.dbapi.get_version_status(
            "name1", product_version_id)
        self.assertIsNotNone(created_version_status)

    def test_get_all_status_by_version_id(self):
        self._create_product_version_status_deps(**self.version_status_deps)
        product_version_id = self.dbapi.get_all_product_versions(
            product_name="product1")[0].id

        self.dbapi.create_platform(name="name2", location="location2",
                                   contact="plat_contact2",
                                   tenant_id="tenant1")
        self.dbapi.add_version_status("name1", product_version_id,
                                      models.Status.NOT_TESTED,
                                      "swift://localhost/deployment")
        self.dbapi.add_version_status("name2", product_version_id,
                                      models.Status.NOT_TESTED,
                                      "swift://localhost2/deployment")
        all_version_status = self.dbapi.get_all_status_by_version_id(
            product_version_id)
        self.assertEqual(2, len(all_version_status))

    def test_non_existing_product_status(self):
        self.assertRaises(exception.ProductVersionStatusNotFound,
                          self.dbapi.get_version_status, "name2", 3)

    def test_update_product_status(self):
        self._create_product_version_status_deps(**self.version_status_deps)
        product_version_id = self.dbapi.get_all_product_versions(
            product_name="product1")[0].id

        self.dbapi.add_version_status("name1", product_version_id,
                                      models.Status.NOT_TESTED,
                                      "swift://localhost/deployment")

        self.dbapi.update_version_status("name1", product_version_id,
                                         models.Status.SUCCESS,
                                         "swift://localhost/deploymentlogs")

        created_version_status = self.dbapi.get_version_status(
            "name1", product_version_id)

        self.assertEqual(models.Status.SUCCESS, created_version_status.status)
        self.assertEqual("swift://localhost/deploymentlogs",
                         created_version_status.logs_location)

    def test_delete_product_status(self):
        self._create_product_version_status_deps(**self.version_status_deps)
        product_version_id = self.dbapi.get_all_product_versions(
            product_name="product1")[0].id

        all_product_status = self.dbapi.get_all_versions_status()
        self.assertEqual(0, len(all_product_status))

        self.dbapi.add_version_status("name1", product_version_id,
                                      models.Status.NOT_TESTED,
                                      "swift://localhost/deployment")
        all_product_status = self.dbapi.get_all_versions_status()
        self.assertEqual(1, len(all_product_status))

        self.dbapi.delete_version_status("name1", product_version_id)
        all_product_status = self.dbapi.get_all_versions_status()
        self.assertEqual(0, len(all_product_status))
