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
from oslo.config import cfg
from pecan import hooks

from saladier.openstack.common import context


class ConfigHook(hooks.PecanHook):
    """Attach the configuration object to the request.

    That allows controllers to get it.
    """

    def before(self, state):
        state.request.cfg = cfg.CONF


class DBHook(hooks.PecanHook):

    def __init__(self, db_connection):
        self.db_connection = db_connection

    def before(self, state):
        state.request.db_conn = self.db_connection


class ContextHook(hooks.PecanHook):
    """Configures a request context and attaches it to the request.

    The following HTTP request headers are used:

    X-User-Id or X-User:
        Used for context.user_id.

    X-Tenant-Id or X-Tenant:
        Used for context.tenant.

    X-Auth-Token:
        Used for context.auth_token.

    X-Roles:
        Used for setting context.is_admin flag to either True or False.
        The flag is set to True, if X-Roles contains either an administrator
        or admin substring. Otherwise it is set to False.

    """
    def __init__(self, public_api_routes):
        self.public_api_routes = public_api_routes
        super(ContextHook, self).__init__()

    def before(self, state):
        user_id = state.request.headers.get('X-User-Id')
        user_id = state.request.headers.get('X-User', user_id)
        tenant = state.request.headers.get('X-Tenant-Id')
        auth_token = state.request.headers.get('X-Auth-Token')

        # TODO(chmouel): openstack policy based
        is_admin = ('admin' in
                    state.request.headers.get('X-Roles', '').split(','))

        state.request.context = context.RequestContext(
            auth_token=auth_token,
            user=user_id,
            tenant=tenant,
            is_admin=is_admin)
