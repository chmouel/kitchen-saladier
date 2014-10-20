# -*- coding: utf-8 -*-
# Copyright (C) 2013 eNovance SAS <licensing@enovance.com>
#
# Author: Chmouel Boudjnah <chmouel@enovance.com>
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
from saladier.tests.api import v1


class TestProducts(v1.FunctionalTest):
    def setUp(self):
        super(TestProducts, self).setUp()

    def test_all_products(self):
        data = self.get_json('/products/')
        self.assertEqual({'products': []}, data)

    def test_product_crud(self):
        prod_dict = dict(name="name1",
                         team="team1",
                         contact="product@owner.org")
        self.post_json("/products/", prod_dict)
        data = self.get_json('/products/')
        self.assertEqual(1, len(data['products']))
        self.assertEqual('product@owner.org', data['products'][0]['contact'])
        self.assertEqual('name1', data['products'][0]['name'])
        self.assertEqual('team1', data['products'][0]['team'])
