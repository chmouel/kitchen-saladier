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
from saladier_integrationtests.common import clients
from saladier_integrationtests.common import config
from saladier_integrationtests.restgen import models as m
import saladierclient.tests.v1.fakes as f


class RestGen(object):
    def __init__(self, manager):
        self.manager = manager

    def run(self):
        public = m.PublicInformation(self.manager)
        public.generate()

        #
        pc = m.ProductCreate(self.manager)
        pc.generate()

        #
        pn = m.ProductShow(self.manager)
        pn.generate()
        product_id = pn.json_resp['id']

        #
        pv = m.ProductVersionCreate(self.manager)
        pv.data['product_id'] = product_id
        pv.generate()

        #
        pfmc = m.PlatformCreate(self.manager)
        pfmc.data['tenant_id'] = self.manager.user_tenant_id
        pfmc.generate()

        #
        platforms = m.PlatformList(self.manager)
        platforms.generate()
        platform_id = platforms.json_resp['platforms'][0]['id']

        #
        st = m.SubscribtionCreate(self.manager)
        st.data['tenant_id'] = self.manager.user_tenant_id
        st.data['product_id'] = product_id
        st.generate()

        #
        pl = m.ProductList(self.manager)
        pl.generate()

        #
        pversion = m.ProductShowVersion(self.manager)
        pversion.dynamic_url = (f.CREATE_PRODUCT['name'] + "/" +
                                f.CREATE_PRODUCT_VERSIONS['version'])
        pversion.generate()
        product_version_id = pversion.json_resp['id']

        #
        status_add = m.StatusAdd(self.manager)
        status_add.data['platform_id'] = platform_id
        status_add.data['product_version_id'] = product_version_id
        status_add.generate()

        #
        status_show = m.StatusShow(self.manager)
        status_show.dynamic_url = platform_id + "/" + product_version_id
        status_show.generate()

        #
        status_update = m.StatusUpdate(self.manager)
        status_update.data['platform_id'] = platform_id
        status_update.data['product_version_id'] = product_version_id
        status_update.data['status'] = "SUCCESS"
        status_update.generate()

        #
        status_delete = m.StatusDelete(self.manager)
        status_delete.dynamic_url = platform_id + "/" + product_version_id
        status_delete.generate()

        #
        sub_delete = m.SubscriptionDelete(self.manager)
        sub_delete.dynamic_url = product_id + "/" + self.manager.user_tenant_id
        sub_delete.generate()

        #
        pv_delete = m.ProductVersionDelete(self.manager)
        pv_delete.dynamic_url = product_id + "/" + product_version_id
        pv_delete.generate()

        #
        product_delete = m.ProductDelete(self.manager)
        product_delete.dynamic_url = product_id
        product_delete.generate()

        #
        platform_delete = m.PlatformDelete(self.manager)
        platform_delete.dynamic_url = platform_id
        platform_delete.generate()


if __name__ == '__main__':
    conf = config.init_conf(True)
    manager = clients.ClientManager(conf)
    gen = RestGen(manager)
    gen.run()
