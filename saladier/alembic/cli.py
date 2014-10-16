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
import sys

from alembic import command
from alembic import config
from oslo.config import cfg
from oslo.db import options
from oslo.db.sqlalchemy import session as db_session
import sqlalchemy

from saladier.db.sqlalchemy import models
from saladier.openstack.common import log

LOG = log.getLogger(__name__)

CONF = cfg.CONF


def init_database():
    # Get the engine from the oslo db configuration.
    engine_facade = db_session.EngineFacade.from_config(CONF)

    # If we are not able to get a session then the tests with the
    # database will be skipped.
    try:
        engine_facade.get_session()
    except Exception:
        LOG.info("database unit tests relative will be skipped")
        return False

    # Then we create the schemas and run alembic to stamp the database with
    # an Alembic version.
    models.BASE.metadata.create_all(engine_facade.get_engine())
    module_abs_path = os.path.abspath(__file__)
    module_dir_abs_path = os.path.dirname(module_abs_path)
    alembic_ini_path = "%s/alembic.ini" % module_dir_abs_path

    alembic_cfg = config.Config(alembic_ini_path)
    alembic_cfg.saladier_config = CONF
    command.stamp(alembic_cfg, "head")


def ensure_database_is_created():
    connection_url = CONF.database.connection
    engine = sqlalchemy.create_engine(connection_url.replace('saladier', ''))
    try:
        conn = engine.connect()
        conn.execute('DROP DATABASE IF EXISTS saladier;')
        conn.execute('CREATE DATABASE saladier;')
        conn.commit()
    except Exception:
        return


def main():
    CONF(sys.argv[1:])
    CONF.register_opts(options.database_opts, 'database')

    ensure_database_is_created()
    ret = init_database()
    if ret is False:
        sys.exit(1)
