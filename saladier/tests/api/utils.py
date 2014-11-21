# -*- coding: utf-8 -*-
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
import datetime
import json

ADMIN_TOKEN = '4562138218392831'
ADMIN_TENANT_ID = '123i2910'
ADMIN_TENANT_NAME = 'admin'

MEMBER_TOKEN = '4562138218392832'
MEMBER_TENANT_ID = '111111i111111'
MEMBER_TENANT_NAME = 'member'

MEMBER_OTHER_TOKEN = '292829821902'
MEMBER_OTHER_TENANT_ID = '22222i22222'
MEMBER_OTHER_TENANT_NAME = 'other'


class FakeMemcache(object):
    """Fake cache that is used for keystone tokens lookup."""

    _cache = {
        'tokens/%s' % ADMIN_TOKEN: {
            'access': {
                'token': {'id': ADMIN_TOKEN,
                          'expires': '2100-09-11T00:00:00'},
                'user': {'id': 'user_id1',
                         'name': 'user_name1',
                         'tenantId': ADMIN_TENANT_ID,
                         'tenantName': ADMIN_TENANT_NAME,
                         'roles': [{'name': 'admin'}]},
            }
        },
        'tokens/%s' % MEMBER_TOKEN: {
            'access': {
                'token': {'id': MEMBER_TOKEN,
                          'expires': '2100-09-11T00:00:00'},
                'user': {'id': 'user_id2',
                         'name': 'user_name',
                         'tenantId': MEMBER_TENANT_ID,
                         'tenantName': MEMBER_TENANT_NAME,
                         'roles': [{'name': 'Member'}]},
            }
        },
        'tokens/%s' % MEMBER_OTHER_TOKEN: {
            'access': {
                'token': {'id': MEMBER_OTHER_TOKEN,
                          'expires': '2100-09-11T00:00:00'},
                'user': {'id': 'user_id2',
                         'name': 'user-other',
                         'tenantId': MEMBER_OTHER_TENANT_ID,
                         'tenantName': MEMBER_OTHER_TENANT_NAME,
                         'roles': [{'name': 'Member'}]},
            }
        }
    }

    def __init__(self):
        self.set_key = None
        self.set_value = None
        self.token_expiration = None

    def get(self, key):
        dt = datetime.datetime.utcnow() + datetime.timedelta(minutes=5)
        return json.dumps((self._cache.get(key), dt.isoformat()))

    def set(self, key, value, time=0, min_compress_len=0):
        self.set_value = value
        self.set_key = key
