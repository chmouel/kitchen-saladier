#
# Copyright 2012 New Dream Network, LLC (DreamHost)
#
# Author: Doug Hellmann <doug.hellmann@dreamhost.com>
#         Angus Salkeld <asalkeld@redhat.com>
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
