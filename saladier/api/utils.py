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
import pecan


class SessionHandler(object):
    def __init__(self):
        self.session = None

    def __enter__(self):
        return self.get_session()

    def __exit__(self, ttype, value, traceback):
        self.close_session()

    def get_session(self):
        if not self.session:
            self.session = pecan.request.db_conn.get_session()
            self.session.begin()
        return self.session

    def close_session(self):
        self.session.commit()
        self.session.close()
