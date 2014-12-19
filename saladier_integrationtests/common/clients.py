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
import saladierclient.client


class ClientManager(object):
    default_saladier_version = 1

    def __init__(self, conf):
        self.conf = conf

        self.user_client = self._get_user_saladier_client()
        x = self.user_client.http_client.auth_ref
        self.user_tenant_id = x['token']['tenant']['id']

        self.admin_client = self._get_admin_saladier_client()
        x = self.admin_client.http_client.auth_ref
        self.admin_tenant_id = x['token']['tenant']['id']

    def _get_user_saladier_client(self):
        return saladierclient.client.get_client(
            self.default_saladier_version,
            os_username=self.conf.user_name,
            os_password=self.conf.user_password,
            os_auth_url=self.conf.auth_url,
            insecure=True,  # TODO(chmou): Put in a Setting
            os_tenant_name=self.conf.user_tenant_name)

    def _get_admin_saladier_client(self):
        return saladierclient.client.get_client(
            self.default_saladier_version,
            os_username=self.conf.admin_name,
            os_password=self.conf.admin_password,
            os_auth_url=self.conf.auth_url,
            insecure=True,  # TODO(chmou): Put in a Setting
            os_tenant_name=self.conf.admin_tenant_name)
