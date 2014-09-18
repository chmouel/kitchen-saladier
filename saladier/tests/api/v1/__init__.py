#
# Copyright 2012 New Dream Network, LLC (DreamHost)
#
# Author: Doug Hellmann <doug.hellmann@dreamhost.com>
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

from saladier.tests import api


class FunctionalTest(api.FunctionalTest):
    PATH_PREFIX = '/v1'


# We have to do this due of lp:1372484 bug when this will be fixed we
# can remove that mock.
class FixedMiniResp(object):
    def __init__(self, error_message, env, headers=[]):
        if env['REQUEST_METHOD'] == 'HEAD':
            self.body = ['']
        else:
            self.body = [error_message.encode()]
        self.headers = list(headers)
        self.headers.append(('Content-type', 'text/plain'))
