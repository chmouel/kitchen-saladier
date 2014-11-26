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
import os
import shutil

import fixtures
from oslo.config import cfg

from saladier.db import api as sqla_api
from saladier.db.sqlalchemy import migration
from saladier.db.sqlalchemy import models
from saladier.tests import base

CONF = cfg.CONF

_DB_CACHE = None

PYBASEDIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../'))


class Database(fixtures.Fixture):
    def _state_path_rel(self, *args):
        return os.path.join(PYBASEDIR, *args)

    def __init__(self, db_api, db_migrate, sql_connection,
                 sqlite_db, sqlite_clean_db):
        self.sql_connection = sql_connection
        self.sqlite_db = sqlite_db
        self.sqlite_clean_db = sqlite_clean_db

        self.engine = db_api.get_engine()
        self.engine.dispose()
        conn = self.engine.connect()

        if sql_connection == "sqlite://":
            self.setup_sqlite(db_migrate)
        elif sql_connection.startswith('sqlite:///'):
            testdb = self._state_path_rel(sqlite_db)
            if os.path.exists(testdb):
                return
            self.setup_sqlite(db_migrate)
        else:
            db_migrate.upgrade('head')
        self.post_migrations()
        if sql_connection == "sqlite://":
            conn = self.engine.connect()
            self._DB = "".join(line for line in conn.connection.iterdump())
            self.engine.dispose()
        else:
            cleandb = self._state_path_rel(sqlite_clean_db)
            shutil.copyfile(testdb, cleandb)

    def setup_sqlite(self, db_migrate):
        if db_migrate.version():
            return
        models.Base.metadata.create_all(self.engine)
        db_migrate.stamp('head')

    def setUp(self):
        super(Database, self).setUp()

        if self.sql_connection == "sqlite://":
            conn = self.engine.connect()
            conn.connection.executescript(self._DB)
            self.addCleanup(self.engine.dispose)
        else:
            shutil.copyfile(self._state_path_rel(self.sqlite_clean_db),
                            self._state_path_rel(self.sqlite_db))
            self.addCleanup(os.unlink, self.sqlite_db)

    def post_migrations(self):
        """Any addition steps that are needed outside of the migrations."""


class DbTestCase(base.TestCase):

    def setUp(self):
        super(DbTestCase, self).setUp()

        self.dbapi = sqla_api.get_backend()

        global _DB_CACHE
        if not _DB_CACHE:
            _DB_CACHE = Database(sqla_api, migration,
                                 sql_connection=CONF.database.connection,
                                 sqlite_db=CONF.database.sqlite_db,
                                 sqlite_clean_db='clean.sqlite')

        self.useFixture(_DB_CACHE)
