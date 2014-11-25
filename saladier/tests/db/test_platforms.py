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


class PlatformTestCase(base.DbTestCase):
    def test_create_platform(self):
        product_name = 'test_create_platform'
        self.dbapi.create_platform(name=product_name, location="location1",
                                   contact="contact1", tenant_id="tenant1")
        platform = self.dbapi.get_platform_by_name(product_name)
        self.assertEqual(product_name, platform["name"])
        self.assertEqual("location1", platform["location"])
        self.assertEqual("contact1", platform["contact"])
        self.assertEqual("tenant1", platform["tenant_id"])

    def test_delete_platform(self):
        product_name = 'test_delete_platform'
        self.dbapi.create_platform(name=product_name, location="location1",
                                   contact="contact1", tenant_id="tenant1")
        self.dbapi.delete_platform_by_name(product_name)
        self.assertRaises(exception.PlatformNotFound,
                          self.dbapi.get_platform_by_name,
                          product_name)

    def test_get_platform_notfound(self):
        self.assertRaises(exception.PlatformNotFound,
                          self.dbapi.get_platform_by_name,
                          "name2")

    def test_create_product_conflict(self):
        product_name = 'test_product_conflict'
        self.dbapi.create_platform(name=product_name, location="location1",
                                   contact="contact1", tenant_id="tenant1")
        self.assertRaises(exception.PlatformAlreadyExists,
                          self.dbapi.create_platform, name=product_name,
                          location="location1", contact="contact1",
                          tenant_id="tenant1")
