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


class Platform(base.APIBase):
    fields = ['id', 'name', 'location', 'contact', 'tenant_id']


class PlatformCollection(base.APIBaseCollections):
    _type = Platform
    dict_field = 'platforms'


class PlatformController(base.BaseRestController):
    @pecan.expose('json')
    def get(self, id):
        try:
            p = Platform(pecan.request.db_conn.get_platform(id))
            return p.as_dict()
        except exception.PlatformNotFound:
            pecan.response.status = 404
            return "Platform %s was not found" % id

    @pecan.expose('json')
    def get_all(self):
        platforms = pecan.request.db_conn.get_all_platforms()
        p = PlatformCollection(platforms)
        return p.as_dict()

    @pecan.expose('json')
    def post(self, name, location, contact, tenant_id):
        if not pecan.request.context.is_admin:
            return webob.exc.HTTPForbidden()

        try:
            pecan.request.db_conn.create_platform(
                name=name, location=location, contact=contact,
                tenant_id=tenant_id)
            pecan.response.status = 201
        except exception.PlatformAlreadyExists:
            pecan.response.status = 409
            return "Platform %s already exist" % name

    @pecan.expose()
    def delete(self, id):
        if not pecan.request.context.is_admin:
            return webob.exc.HTTPForbidden()
        pecan.request.db_conn.delete_platform(id=id)
        pecan.response.status = 204
