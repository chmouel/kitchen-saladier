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
import inspect
import json
import re

API_VERSION = 'v1'


class Base(object):
    response = None
    json_resp = None
    data = None
    documentation_type = None
    url_doc = None
    dynamic_url = None

    def __init__(self, manager):
        self.manager = manager

    def generate(self):
        if self.admin:
            req = self.manager.admin_client.http_client.raw_request
        else:
            req = self.manager.user_client.http_client.raw_request

        if self.dynamic_url and self.base_url:
            _url = self.base_url + "/" + self.dynamic_url
        else:
            _url = self.url

        if _url == "/":
            target_url = "/"
        else:
            target_url = "/%s/%s" % (API_VERSION, _url)

        self.response, body = req(self.method, target_url,
                                  headers={'Content-Type': 'application/json'},
                                  body=json.dumps(self.data))
        body = body.read()
        if body:
            self.json_resp = json.loads(body)
        self._generate_rest()

    def _convert_json_and_adjust(self, data):
        ret = ""
        if data:
            data = json.dumps(data, indent=8)[:-1] + "    }"
            # UUID
            ret = re.sub(r'(\w{8}(-\w{4}){3}-\w{12}?)',
                         'GENERATED_UUID', data)
            # Tenant_ID
            ret = re.sub(r'[a-z0-9]{32}', 'TENANT_ID', ret)

            # DATETIME
            ret = re.sub("\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}",
                         'DATETIME', ret)
        return "    " + ret.replace(" \n", "\n") + "\n\n"

    # TODO(chmou): use a proper templates instead
    def _generate_rest(self):
        documentation = inspect.getdoc(self)

        url = self.url.startswith("/") and self.url or "/" + self.url

        with open("%s/%s.rst" % (self.manager.conf.documentation_output_dir,
                                 self.documentation_type), "w") as f:
            title = "%s %s" % (self.method.upper(), self.url_doc or url)
            f.write(title + "\n")
            f.write("=" * len(title) + "\n\n")
            f.write(documentation + "\n\n")
            if self.data:
                f.write("Arguments::\n\n")
                f.write(self._convert_json_and_adjust(self.data))
            f.write("Returns::\n\n")
            f.write("    %s\n\n" % self.response.status)
            if self.method.upper() == "GET":
                f.write(self._convert_json_and_adjust(self.json_resp))
            if self.admin:
                f.write(".. note:: This call needs to be made with the admin"
                        " rights.\n")
