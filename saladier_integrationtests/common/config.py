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

from oslo.config import cfg

import saladier_integrationtests


IntegrationTestGroup = [
    cfg.StrOpt('user_name',
               default=os.environ.get('SALADIER_USERNAME'),
               help="Username to use for API requests."),
    cfg.StrOpt('user_password',
               default=os.environ.get('SALADIER_PASSWORD'),
               help="API key to use when authenticating.",
               secret=True),
    cfg.StrOpt('user_tenant_name',
               default=os.environ.get('SALADIER_TENANT_NAME'),
               help="Tenant name to use for API requests."),
    cfg.StrOpt('admin_name',
               default=os.environ.get('SALADIER_ADMIN_USERNAME'),
               help="Username to use for API requests."),
    cfg.StrOpt('admin_password',
               default=os.environ.get('SALADIER_ADMIN_PASSWORD'),
               help="API key to use when authenticating.",
               secret=True),
    cfg.StrOpt('admin_tenant_name',
               default=os.environ.get('SALADIER_ADMIN_TENANT_NAME'),
               help="Tenant name to use for API requests."),
    cfg.StrOpt('auth_url',
               default=os.environ.get('SALADIER_AUTH_URL'),
               help="Full URI of the OpenStack Identity API (Keystone), v2"),
]


def list_opts():
    return [
        ("", IntegrationTestGroup)]


def init_conf(read_conf=True):
    default_config_files = None
    if read_conf:
        confpath = os.environ.get("SALADIER_INTEG_CONF")

        if not confpath:
            confpath = os.path.join(
                os.path.dirname(os.path.realpath(
                    saladier_integrationtests.__file__)),
                "..",
                "etc",
                "saladier",
                "saladier_integration.conf.sample",
            )
        if os.path.isfile(confpath):
            default_config_files = [confpath]

    conf = cfg.ConfigOpts()
    conf(args=[], project='saladier_integrationtests',
         default_config_files=default_config_files)

    for opt in IntegrationTestGroup:
        conf.register_opt(opt)
    return conf
