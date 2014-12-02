# -*- coding: utf-8 -*-
# Author: Chmouel Boudjnah <chmouel.boudjnah@enovance.com>
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


class Subscription(base.APIBase):
    fields = ['id', 'tenant_id', 'product_id']


class SubscriptionCollection(base.APIBaseCollections):
    _type = Subscription
    dict_field = 'subscriptions'


class SubscriptionController(base.BaseRestController):
    @pecan.expose('json')
    def post(self, tenant_id, product_id):
        if not pecan.request.context.is_admin:
            return webob.exc.HTTPForbidden()

        try:
            pecan.request.db_conn.create_subscription(tenant_id, product_id)
            pecan.response.status = 201
        except exception.SubscriptionAlreadyExists:
            pecan.response.status = 409

    @pecan.expose()
    def delete(self, product_id, tenant_id):
        if not pecan.request.context.is_admin:
            return webob.exc.HTTPForbidden()
        pecan.request.db_conn.delete_subscription(product_id, tenant_id)
        pecan.response.status = 204

    @pecan.expose('json')
    def get(self, tenant_id):
        # TODO(chmou): we need to scope that by tenant to have his view, we
        # don't yet so we just restrict it to admins
        if not pecan.request.context.is_admin:
            return webob.exc.HTTPForbidden()
        subscriptions = pecan.request.db_conn.get_subscriptions_for_tenant_id(
            tenant_id)
        p = SubscriptionCollection(subscriptions)
        return p.as_dict()
