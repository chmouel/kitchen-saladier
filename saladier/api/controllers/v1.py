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
from pecan import rest

import saladier.api.utils as api_utils
from saladier.openstack.common import log

LOG = log.getLogger(__name__)


class BaseRestController(rest.RestController):
    def __init__(self):
        super(BaseRestController, self).__init__()


class TestController(rest.RestController):
    @pecan.expose('json')
    def index(self):
        return dict(foo='bar')


class ProductController(BaseRestController):

    @pecan.expose('json')
    def get_all(self):
        session = pecan.request.db_conn.get_session()
        return pecan.request.db_conn.get_all_products(session)

    @pecan.expose('json')
    # TODO(chmou): figure out what the deal
    # with that first empty argument given by pecan
    def post(self, _, name, team, contact):
        with api_utils.SessionHandler() as session:
            pecan.request.db_conn.create_product(
                session, name=name, team=team, contact=contact)


class V1Controller(object):
    """Version 1 API controller root."""

    test = TestController()
    products = ProductController()
