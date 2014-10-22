# -*- coding: utf-8 -*-
# Copyright (C) 2014 eNovance SAS <licensing@enovance.com>
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
import pecan

import saladier.api.controllers.base as base


class Product(base.APIBase):
    fields = ['name', 'contact', 'team']


class ProductCollection(base.APIBaseCollections):
    _type = Product
    dict_field = 'products'


class ProductController(base.BaseRestController):

    @pecan.expose('json')
    def get_all(self):
        products = pecan.request.db_conn.get_all_products()
        p = ProductCollection(products)
        return p.as_dict()

    @pecan.expose('json')
    # TODO(chmou): figure out what the deal
    # with that first empty argument given by pecan
    def post(self, _, name, team, contact):
        pecan.request.db_conn.create_product(
            name=name, team=team, contact=contact)
