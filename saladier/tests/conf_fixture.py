# Copyright 2010 United States Government as represented by the
# Administrator of the National Aeronautics and Space Administration.
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.
import os

import fixtures
from oslo.config import cfg

CONF = cfg.CONF


class ConfFixture(fixtures.Fixture):
    """Fixture to manage global conf settings."""

    def __init__(self, conf):
        self.conf = conf

    def setUp(self):
        super(ConfFixture, self).setUp()

        test_cnx = os.environ.get("SALADIER_DATABASE_TEST_CONNECTION")
        if test_cnx:
            self.conf.set_default('connection', test_cnx, group='database')
        else:
            self.conf.set_default('connection', "sqlite://", group='database')
            self.conf.set_default('sqlite_synchronous', False,
                                  group='database')
            self.conf.set_default('verbose', True)
            self.addCleanup(self.conf.reset)
