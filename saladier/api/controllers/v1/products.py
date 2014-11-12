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
import webob

import saladier.api.controllers.base as base
import saladier.common.exception as exception


class Product(base.APIBase):
    fields = ['name', 'contact', 'team']


class ProductCollection(base.APIBaseCollections):
    _type = Product
    dict_field = 'products'


class ProductController(base.BaseRestController):
    @pecan.expose('json')
    def get(self, name):
        try:
            p = Product(pecan.request.db_conn.get_product_by_name(name))
            return p.as_dict()
        except exception.ProductNotFound:
            pecan.response.status = 404
            return "Product %s was not found" % name

    @pecan.expose('json')
    def get_all(self):
        products = pecan.request.db_conn.get_all_products()
        p = ProductCollection(products)
        return p.as_dict()

    @pecan.expose()
    # TODO(chmou): There is a bug in pecan with /foo/bar/, it's fixed here
    # https://review.openstack.org/#/c/131410/, we keep an empty _ for the
    # first of our function until this get released in a pecan release that
    # we can use.
    def post(self, _, name, team, contact):
        if not pecan.request.context.is_admin:
            return webob.exc.HTTPForbidden()

        try:
            pecan.request.db_conn.create_product(
                name=name, team=team, contact=contact)
            pecan.response.status = 201
        except exception.ProductAlreadyExists:
            pecan.response.status = 409
            return "Product %s already exist" % name

    @pecan.expose()
    def delete(self, name):
        if not pecan.request.context.is_admin:
            return webob.exc.HTTPForbidden()
        pecan.request.db_conn.delete_product_by_name(name=name)
        pecan.response.status = 204
