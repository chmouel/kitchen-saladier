#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (C) 2014 eNovance SAS <licensing@enovance.com>
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.
import socket
import time

from keystoneclient.v2_0 import client as keystone_client


def wait_service_is_up(service, url, port):

    max_retry = 12

    for i in xrange(max_retry):
        try:
            service_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            service_socket.connect((url, port))
        except socket.error:
            if i == (max_retry - 1):
                print("Could not connect to %s after %s retries, "
                      "please investigate locally with fig logs command..." %
                      (service, max_retry))
                raise Exception("Could not connect")
            else:
                print("[%s] Waiting that %s on %s:%s is started, will retry "
                      "in 5 seconds..." % (i, service, url, port))
                time.sleep(5)
    print("\033[32m" + "%s is up :-) !" % service + "\033[0m")


def authenticate(auth_url, tenant_name, username, password):

    k_client = keystone_client.Client(auth_url=auth_url,
                                      tenant_name=tenant_name,
                                      username=username,
                                      password=password)

    return k_client.auth_token, k_client.tenant_id