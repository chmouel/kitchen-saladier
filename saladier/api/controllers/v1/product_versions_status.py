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


class ProductVersionsStatus(base.APIBase):
    fields = ['product_version_id', 'platform_name', 'status', 'logs_location']


class ProductVersionStatusCollection(base.APIBaseCollections):
    _type = ProductVersionsStatus
    dict_field = 'product_versions_status'


class ProductVersionsStatusController(base.BaseRestController):

    @pecan.expose()
    def post(self, platform_name, product_version_id, status, logs_location):

        platform = pecan.request.db_conn.get_platform_by_name(platform_name)

        if ((platform.tenant_id != pecan.request.context.tenant) and
                not pecan.request.context.is_admin):
            return webob.exc.HTTPForbidden()

        try:
            pecan.request.db_conn.add_version_status(platform_name,
                                                     product_version_id,
                                                     status,
                                                     logs_location)
            pecan.response.status = 201
        except exception.ProductVersionStatusAlreadyExists:
            pecan.response.status = 409

    @pecan.expose()
    def delete(self, platform_name, product_version_id):
        platform = pecan.request.db_conn.get_platform_by_name(platform_name)

        if ((platform.tenant_id != pecan.request.context.tenant) and
                not pecan.request.context.is_admin):
            return webob.exc.HTTPForbidden()

        pecan.request.db_conn.delete_version_status(platform_name,
                                                    product_version_id)
        pecan.response.status = 204

    @pecan.expose()
    def put(self, platform_name, product_version_id, new_status,
            new_logs_location):
        platform = pecan.request.db_conn.get_platform_by_name(platform_name)

        if ((platform.tenant_id != pecan.request.context.tenant) and
                not pecan.request.context.is_admin):
            return webob.exc.HTTPForbidden()

        try:
            pecan.request.db_conn.update_version_status(platform_name,
                                                        product_version_id,
                                                        new_status,
                                                        new_logs_location)
            pecan.response.status = 204
        except exception.ProductVersionStatusNotFound:
            pecan.response.status = 404

    @pecan.expose('json')
    def get(self, platform_name, product_version_id):
        try:
            platform = pecan.request.db_conn.get_platform_by_name(
                platform_name)
        except exception.PlatformNotFound:
            pecan.response.status = 404
            return

        if ((platform.tenant_id != pecan.request.context.tenant) and
                not pecan.request.context.is_admin):
            return webob.exc.HTTPForbidden()

        try:
            pvs = ProductVersionsStatus(
                pecan.request.db_conn.get_version_status(platform_name,
                                                         product_version_id))
            pecan.response.status = 200
            return pvs.as_dict()
        except exception.ProductVersionStatusNotFound:
            pecan.response.status = 404
