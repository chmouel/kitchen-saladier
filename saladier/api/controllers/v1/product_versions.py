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
import pecan
import webob

import saladier.api.controllers.base as base
import saladier.common.exception as exception


class ProductVersions(base.APIBase):
    fields = ['product_name', 'version', 'uri']


class ProductCollection(base.APIBaseCollections):
    _type = ProductVersions
    dict_field = 'versions'


class ProductVersionsController(base.BaseRestController):
    @pecan.expose()
    # TODO(chmou): There is a bug in pecan with /foo/bar/, it's fixed here
    # https://review.openstack.org/#/c/131410/, we keep an empty _ for the
    # first arg of our function until this get released in a pecan release that
    # we can use.
    def post(self, _, product, version, url):
        if not pecan.request.context.is_admin:
            return webob.exc.HTTPForbidden()

        try:
            pecan.request.db_conn.create_product_version(
                product, version, url)
            pecan.response.status = 201
        except exception.ProductVersionAlreadyExists:
            pecan.response.status = 409
            return "Product %s already exist" % product

    @pecan.expose()
    def delete(self, product, version):
        if not pecan.request.context.is_admin:
            return webob.exc.HTTPForbidden()

        pecan.request.db_conn.delete_product_versions(
            product, version)
        pecan.response.status = 204

    @pecan.expose('json')
    def get(self, product):
        products = pecan.request.db_conn.get_all_product_versions(product)
        p = ProductCollection(products)
        return p.as_dict()
