# -*- coding: utf-8 -*-
# Copyright (C) 2013 eNovance SAS <licensing@enovance.com>
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
from oslo.db import options as db_options

from saladier.db import api as api_db
from saladier.openstack.common import log

LOG = log.getLogger(__name__)

cfg.CONF.register_opts([], group='database')
db_options.set_defaults(cfg.CONF)
cfg.CONF.import_opt('connection', 'oslo.db.options', group='database')


def get_connection(conf):
    dbconn = api_db.DbApi(conf)
    dbconn.connect()
    return dbconn
