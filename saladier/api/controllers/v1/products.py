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
    fields = ['name', 'contact', 'team']
    dict_field = 'versions'

    def version_info(self, specific_version=None):
        # NOTE(chmou): We have those pv_gad/pv_gas cause 80 lines sucks!
        pv_gad = pecan.request.db_conn.get_all_product_versions
        pv_gas = pecan.request.db_conn.get_all_status_by_version_id
        ret = {}
        for version in pv_gad(self.name):
            ret[version.version] = {
                'id': version.id,
                # TODO(chmou): placeholder, we will need to have that updated
                # properly when will have a decision maker API (tm)
                'ready_for_deploy': False,
                # TODO(chmou): placeholder we will add all the platforms here
                # where that product_version has been validated on.
                'validated_on': pv_gas(version.id)
            }

        if specific_version and specific_version in ret:
            return ret[specific_version]
        elif not specific_version:
            return ret
        else:
            raise exception.ProductVersionNotFound(specific_version)

    def as_dict(self):
        return dict(versions=self.version_info(),
                    contact=self.contact,
                    team=self.team)


class ProductCollection(base.APIBaseCollections):
    _type = Product
    dict_field = 'products'

    def as_dict(self):
        # NOTE(chmou): We have that pv_gad cause 80 lines sucks big time!
        pv_gad = pecan.request.db_conn.get_all_product_versions

        # TODO(chmou): we may want to filter only for version when doing the
        # get_all_product_versions call.
        pv_fmt = lambda name: [v['version'] for v in pv_gad(name)]

        return {self.dict_field:
                dict((c.name, pv_fmt(c.name))
                     for c in self.collections)}


class ProductController(base.BaseRestController):
    @pecan.expose('json')
    def get_one(self, name, *args):
        try:
            p = Product(
                pecan.request.db_conn.get_product_by_name(
                    name, tenant_id=pecan.request.context.tenant,
                    admin=pecan.request.context.is_admin))
            # NOTE(chmou): This probably can be optimised in a nicer way, we
            # currently list everything in versions and filter manually in
            # python. There is many way to do that properly in sqla but since I
            # don't masterize let's keep it like that for now.
            if len(args) == 1:
                return p.version_info(args[0])
            else:
                return p.as_dict()
        except (exception.ProductNotFound, exception.ProductVersionNotFound):
            pecan.response.status = 404

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
    def delete(self, name):
        if not pecan.request.context.is_admin:
            return webob.exc.HTTPForbidden()
        pecan.request.db_conn.delete_product_by_name(name=name)
        pecan.response.status = 204
