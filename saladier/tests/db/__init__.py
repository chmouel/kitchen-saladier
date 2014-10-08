# -*- coding: utf-8 -*-
#
# Copyright 2014 eNovance SAS <licensing@enovance.com>
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

import oslo.db

from saladier.db import api
from saladier.db.sqlalchemy import models
from saladier.openstack.common.fixture import config
from saladier.tests import base


class BaseTestDb(base.BaseTestCase):
    """Base test class for database unit tests."""

    db_api = None

    @classmethod
    def setUpClass(cls):
        super(BaseTestDb, cls).setUpClass()
        conf = config.Config().conf
        oslo.db.options.set_defaults(conf)
        conf.set_override('connection',
                          'mysql+pymysql://root@localhost/saladier',
                          group='database')
        BaseTestDb.db_api = api.DbApi(conf)
        BaseTestDb.db_api.connect()
        try:
            BaseTestDb._drop_tables_content()
        except Exception:
            pass

    @classmethod
    def _drop_tables_content(cls):
        session = BaseTestDb.db_api.get_session()
        session.begin()
        for table in reversed(models.BASE.metadata.sorted_tables):
            session.execute(table.delete())
        session.commit()

    @classmethod
    def tearDownClass(cls):
        super(BaseTestDb, cls).tearDownClass()
        BaseTestDb.db_api.disconnect()

    def setUp(self):
        super(BaseTestDb, self).setUp()
        self.db_api = BaseTestDb.db_api
        self.session = self.db_api.get_session()
        self.session.begin()

    def tearDown(self):
        super(BaseTestDb, self).tearDown()
        self.session.rollback()
        self.session.close()
