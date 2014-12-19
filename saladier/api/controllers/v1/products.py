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


class Product(base.APIBase):
    fields = ['id', 'name', 'contact', 'team']
    dict_field = 'versions'

    def version_info(self, product_version_id=None):
        """Return the versions associated with the product.

        :param product_version_id: only return a given version (optional)

        """
        # NOTE(chmou): We have those pv_gad/pv_gas cause 80 lines sucks!
        pv_gad = pecan.request.db_conn.get_all_product_versions
        pv_gas = pecan.request.db_conn.get_all_status_by_version_id
        ret = []
        for version in pv_gad(self.id):
            if product_version_id and version.id != product_version_id:
                continue
            ret.append({
                'id': version.id,
                'version': version.version,
                # TODO(chmou): placeholder, we will need to have that updated
                # properly when will have a decision maker API (tm)
                'ready_for_deploy': False,
                'uri': version.uri,
                # TODO(chmou): placeholder we will add all the platforms here
                # where that product_version has been validated on.
                'validated_on': pv_gas(version.id)
            })
        return ret

    def as_dict(self):
        return dict(id=self.id,
                    versions=self.version_info(),
                    contact=self.contact,
                    name=self.name,
                    team=self.team)


class ProductCollection(base.APIBaseCollections):
    _type = Product
    dict_field = 'products'


class ProductController(base.BaseRestController):
    @pecan.expose('json')
    def get_one(self, id, *args):
        try:
            p = Product(
                pecan.request.db_conn.get_product(
                    id, tenant_id=pecan.request.context.tenant,
                    admin=pecan.request.context.is_admin))
            # NOTE(chmou): This probably can be optimised in a nicer way, we
            # currently list everything in versions and filter manually in
            # python. There is many way to do that properly in sqla but since I
            # don't masterize let's keep it like that for now.
            if len(args) == 1:
                version_id = args[0]
                try:
                    return p.version_info(version_id)[0]
                except IndexError:
                    pecan.response.status = 404
                    return "Version %s of Product %s was not found" % (
                        version_id, id)
            else:
                return p.as_dict()
        except (exception.ProductNotFound, exception.ProductVersionNotFound):
            pecan.response.status = 404
            return "Product %s was not found" % id

    @pecan.expose('json')
    def get_all(self):
        products = pecan.request.db_conn.get_all_products(
            tenant_id=pecan.request.context.tenant,
            admin=pecan.request.context.is_admin)
        p = ProductCollection(products)
        return p.as_dict()

    @pecan.expose('json')
    def post(self, name, team, contact):
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
    def delete(self, id):
        if not pecan.request.context.is_admin:
            return webob.exc.HTTPForbidden()
        pecan.request.db_conn.delete_product(id=id)
        pecan.response.status = 204
