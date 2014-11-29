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

import json
import os
import sys

import requests

import utils as func_utils  # noqa

AUTH_URL = "http://%s:35357/v2.0" % os.getenv("KEYSTONE_PORT_35357_TCP_ADDR")
SALADIER_URL = os.getenv("SALADIER_PORT_8777_TCP_ADDR")
KEYSTONE_URL = os.getenv("KEYSTONE_PORT_35357_TCP_ADDR")

ADMIN_TENANT = "service"
ADMIN_NAME = "saladier_admin"

USER_TENANT = "saladier"
USER_NAME = "saladier_user1"

PASSWORD = os.getenv("SALADIER_USER_PASSWORD")

try:
    func_utils.wait_service_is_up("Keystone", KEYSTONE_URL, 35357)
    func_utils.wait_service_is_up("Saladier", SALADIER_URL, 8777)
except Exception:
    sys.exit(1)

USER_TOKEN, USER_TENANT_ID = func_utils.authenticate(AUTH_URL, USER_TENANT,
                                                     USER_NAME, PASSWORD)
ADMIN_TOKEN, ADMIN_TENANT_ID = func_utils.authenticate(AUTH_URL, ADMIN_TENANT,
                                                       ADMIN_NAME, PASSWORD)


def saladier_request(message, test_type, url, token, method, expected_status,
                     data=None, verbose=True, generate_doc_rests=True,
                     url_doc=None):
    func_method = getattr(requests, method)
    target_url = "http://%s:8777/v1%s" % (SALADIER_URL, url)
    if url == "/":
        target_url = "http://%s:8777" % SALADIER_URL
    headers = {'x-auth-token': token}
    response = func_method(target_url, headers=headers, data=data)

    if verbose:
        if expected_status == response.status_code:
            print("[*] " + message + ". " + "\033[32m" + "SUCCESS" + "\033[0m")
        else:
            print("\033[91m" + "%s. FAILED with status '%s'" %
                  (message, response.status_code) + "\033[0m")
            sys.exit(1)

    if generate_doc_rests:
        with open("/code/doc/source/rests/%s.rst" % test_type, "w") as f:
            title = "%s %s" % (method.upper(), url_doc or url)
            f.write(title + "\n")
            f.write("=" * len(title) + "\n\n")
            f.write(message + "\n\n")
            if data:
                f.write("Arguments::\n\n")
                j_dumps = json.dumps(data, indent=8)[:-1] + "    }"
                f.write("    " + j_dumps.replace(" \n", "\n") + "\n\n")
            f.write("Returns::\n\n")
            f.write("    %s\n\n" % expected_status)
            if method == "get":
                j_dumps = json.dumps(response.json(), indent=8)[:-1] + "    }"
                f.write("    " + j_dumps.replace(" \n", "\n") + "\n\n")
            if token == ADMIN_TOKEN:
                f.write(".. note:: This call needs to be made with the admin"
                        " rights.\n")

    if method == "get":
        return response.json()


print("\033[95m" + "\n*** Starting functional testing ***")
print("-----------------------------------\n" + "\033[0m")

saladier_request("Get saladier public URL with version and location",
                 "public_version_access",
                 "/",
                 ADMIN_TOKEN,
                 "get",
                 200)

saladier_request("Create a product",
                 "product_create",
                 "/products",
                 ADMIN_TOKEN,
                 "post",
                 201,
                 dict(team="boa",
                      name="product1",
                      contact="cedric@isthegreatest.com"))

saladier_request("Associate a product to a version",
                 "product_version_create",
                 "/versions",
                 ADMIN_TOKEN,
                 "post",
                 201,
                 dict(product="product1",
                      url="http://anywhereyoulike",
                      version="1.0"))

saladier_request("Create platform",
                 "platform_create",
                 "/platforms",
                 ADMIN_TOKEN,
                 "post",
                 201,
                 dict(name="platform1",
                      location="ParisEstMagique",
                      contact="thecedric@isthegreatest.com",
                      tenant_id="0000101010101"))

resp = saladier_request("Show created platform",
                        "platform_list",
                        "/platforms/",
                        USER_TOKEN,
                        "get",
                        200)
if resp["platforms"][0]["contact"] != "thecedric@isthegreatest.com":
    print("Not expected created platform '%s'" % resp["platforms"][0])
    sys.exit(1)

saladier_request("Subscribe tenant '%s' to product" % USER_NAME,
                 "product_subscription_create",
                 "/subscriptions",
                 ADMIN_TOKEN,
                 "post",
                 201,
                 dict(product_name="product1",
                      tenant_id=USER_TENANT_ID))

resp = saladier_request("List available products for the current users",
                        "product_list",
                        "/products/",
                        USER_TOKEN,
                        "get",
                        200)
if resp["products"] != dict(product1=['1.0']):
    print("Not expected products '%s'" % resp["products"])
    sys.exit(1)

resp = saladier_request("Show specific product information",
                        "product_get",
                        "/products/product1",
                        USER_TOKEN,
                        "get",
                        200)
if (("1.0" not in resp["versions"]) or
        (not resp["contact"] == "cedric@isthegreatest.com")):
    print("Not expected product information '%s'" % resp)
    sys.exit(1)

resp = saladier_request("Show specific product/version information",
                        "product_get_version",
                        "/products/product1/1.0",
                        USER_TOKEN,
                        "get",
                        200)
if "validated_on" not in resp:
    print("Not expected product version information '%s'" % resp)
    sys.exit(1)

product_version_id = resp["id"]
saladier_request("Add a status to a product version",
                 "product_version_status_add",
                 "/status",
                 ADMIN_TOKEN,
                 "post",
                 201,
                 dict(platform_name='platform1',
                      product_version_id=product_version_id,
                      status="NOT_TESTED",
                      logs_location="swift://localhost/deploy"))

resp = saladier_request("Show product version status",
                        "product_version_status_get",
                        "/status/platform1/%s" % product_version_id,
                        ADMIN_TOKEN,
                        "get",
                        200,
                        url_doc="/status/platform1/product_version_id")
if ((resp["platform_name"] != "platform1") or
        (resp["status"] != "NOT_TESTED") or
        (resp["logs_location"] != "swift://localhost/deploy")):
    print("Not expect product version status '%s'" % resp)
    sys.exit(1)

saladier_request("Update the status of our product version",
                 "product_version_status_update",
                 "/status",
                 ADMIN_TOKEN,
                 "put",
                 204,
                 dict(platform_name='platform1',
                      product_version_id=product_version_id,
                      new_status="SUCCESS",
                      new_logs_location="swift://localhost/deploy_new"))

saladier_request("Delete status of our product",
                 "product_version_status_delete",
                 "/status/platform1/%s" % product_version_id,
                 ADMIN_TOKEN,
                 "delete",
                 204,
                 url_doc="/status/platform1/product_version_id")

saladier_request("Delete subscription of '%s' to our product" % USER_NAME,
                 "product_subscription_delete",
                 "/subscriptions/product1/%s" % USER_TENANT_ID,
                 ADMIN_TOKEN,
                 "delete",
                 204,
                 url_doc="/subscriptions/product1/tenant_id")

saladier_request("Delete Association between product and version",
                 "product_version_delete",
                 "/versions/product1/1.0",
                 ADMIN_TOKEN,
                 "delete",
                 204)

saladier_request("Delete created product",
                 "product_delete",
                 "/products/product1",
                 ADMIN_TOKEN,
                 "delete",
                 204)

saladier_request("Delete created platform",
                 "platform_delete",
                 "/platforms/platform1",
                 ADMIN_TOKEN,
                 "delete",
                 204)

print("\033[32m" + "\nFunctional tests succeeded, congratulations :)")
print("----------------------------------------------\n" + "\033[0m")
