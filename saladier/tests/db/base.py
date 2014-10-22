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
from oslo.config import cfg

from saladier.db import api as sqla_api
from saladier.tests import base

CONF = cfg.CONF


class DbTestCase(base.TestCase):

    def setUp(self):
        super(DbTestCase, self).setUp()

        self.dbapi = sqla_api.get_backend()
        self.engine = sqla_api.get_engine()
        self.engine.dispose()

        # NOTE(chmou): For testing we use the same session every time so we can
        # rollback after
        self.session = sqla_api.get_session(recycle=True)
        self.session.begin()
        self.addCleanup(self._rollback_db)
        self.addCleanup(self.session.close)

    def _rollback_db(self):
        sqla_api.rollback()
