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

import os

import oslo.db
import sqlalchemy

from saladier.db import api
from saladier.db.sqlalchemy import models
from saladier.openstack.common.fixture import config
from saladier.tests import base


DEFAULT_DB_TEST_CONNECTION = 'root@localhost/saladier'


class BaseTestDb(base.BaseTestCase):
    """Base test class for database unit tests."""

    db_api = None

    @classmethod
    def setUpClass(cls):
        super(BaseTestDb, cls).setUpClass()
        BaseTestDb.connected = True
        conf = config.Config().conf
        oslo.db.options.set_defaults(conf)
        # Fig testing see saladier/tools/containers/fig.yml
        if (os.environ.get('DB_PORT_3306_TCP_ADDR') and
           os.environ.get('SALADIER_DB_PASSWORD')):
            db_connection = 'saladier:%s@%s/saladier' % (
                os.environ.get('SALADIER_DB_PASSWORD'),
                os.environ.get('DB_PORT_3306_TCP_ADDR'))
        else:
            db_connection = DEFAULT_DB_TEST_CONNECTION
        conf.set_override('connection',
                          'mysql+pymysql://' + db_connection,
                          group='database')
        BaseTestDb.db_api = api.DbApi(conf)
        try:
            BaseTestDb.db_api.connect()
        except sqlalchemy.exc.OperationalError:
            BaseTestDb.connected = False
            return
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
        if BaseTestDb.connected:
            BaseTestDb.db_api.disconnect()

    def setUp(self):
        super(BaseTestDb, self).setUp()
        self.db_api = BaseTestDb.db_api
        try:
            self.session = self.db_api.get_session()
        except Exception:
            self.skipTest("Error while connecting to mysql")
        self.session.begin()

    def tearDown(self):
        super(BaseTestDb, self).tearDown()
        self.session.rollback()
        self.session.close()
