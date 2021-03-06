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
from saladier.tests.api import utils
import saladier.tests.api.v1.base as base


class TestProductVersions(base.V1FunctionalTest):
    def test_product_version_create(self):
        product_id = self._create_sample_product(name='name1')
        self.assertTrue(product_id)

        for version in ['1.0', '1.1']:
            self._create_sample_product_version(product_id=product_id,
                                                version=version)

    def test_product_version_delete(self):
        product_id = self._create_sample_product(name='name1')
        self._create_sample_product_version(product_id=product_id,
                                            version="1.0")
        self.delete('/versions/%s/1.0' % product_id, status=204)

    def test_product_version_delete_as_user(self):
        product_id = self._create_sample_product(name='name1')
        self._create_sample_product_version(product_id=product_id,
                                            version="1.0")
        self.delete('/versions/%s/1.0' % product_id,
                    headers={'X-Auth-Token': utils.MEMBER_TOKEN},
                    status=403)

    def test_product_version_create_user_denied(self):
        product_id = self._create_sample_product(name='name1')

        version_dict = dict(product_id=product_id,
                            url="http://localhost/",
                            version="1.0")
        self.post_json("/versions",
                       version_dict,
                       headers={'X-Auth-Token': utils.MEMBER_TOKEN},
                       status=403)

    def test_product_version_create_conflicts(self):
        product_id = self._create_sample_product(name='name1')

        version_dict = dict(product_id=product_id,
                            url="http://localhost/",
                            version="1.0")
        self.post_json("/versions",
                       version_dict,
                       status=201)

        self.post_json("/versions",
                       version_dict,
                       status=409)
