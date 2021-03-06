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
    fields = ['id', 'product_id', 'version', 'url']


class ProductCollection(base.APIBaseCollections):
    _type = ProductVersions
    dict_field = 'versions'


class ProductVersionsController(base.BaseRestController):
    @pecan.expose('json')
    def post(self, product_id, version, url):
        if not pecan.request.context.is_admin:
            return webob.exc.HTTPForbidden()

        try:
            pecan.request.db_conn.create_product_version(
                product_id, version, url)
            pecan.response.status = 201
        except exception.ProductVersionAlreadyExists:
            pecan.response.status = 409
            return "Product %s already exist" % product_id

    @pecan.expose()
    def delete(self, product_id, version):
        if not pecan.request.context.is_admin:
            return webob.exc.HTTPForbidden()

        pecan.request.db_conn.delete_product_versions(
            product_id, version)
        pecan.response.status = 204
