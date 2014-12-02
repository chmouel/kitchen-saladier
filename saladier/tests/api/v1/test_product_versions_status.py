# -*- coding: utf-8 -*-
# Copyright (C) 2013 eNovance SAS <licensing@enovance.com>
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
from saladier.db.sqlalchemy import models
from saladier.tests.api import utils
import saladier.tests.api.v1.base as base


class TestProductVersionStatus(base.V1FunctionalTest):
    def setUp(self):
        super(TestProductVersionStatus, self).setUp()

    def test_add_version_status(self):
        product_id = self._create_sample_product(name='name1')
        pv_id = self._create_sample_product_version(product_id=product_id,
                                                    version="1.0")
        platform_id = self._create_sample_platform(
            name='plat1',
            location='location1',
            contact='contact1')

        status_dict = dict(platform_id=platform_id,
                           product_version_id=pv_id,
                           status=models.Status.NOT_TESTED,
                           logs_location="swift://localhost/deploy")
        self.post_json("/status", status_dict, status=201)

    def test_add_version_status_as_user(self):
        product_id = self._create_sample_product(name='name1')
        self._create_sample_product_version(product_id=product_id,
                                            version="1.0")
        pv_id = self._get_product_version_id_by_version_name(product_id, "1.0")
        platform_id = self._create_sample_platform(
            name='plat1', location='location1', contact='contact1')

        status_dict = dict(platform_id=platform_id,
                           product_version_id=pv_id,
                           status=models.Status.NOT_TESTED,
                           logs_location="swift://localhost/deploy")
        self.post_json("/status", status_dict,
                       headers={'X-Auth-Token': utils.MEMBER_TOKEN},
                       status=403)

    def test_add_existing_version_status(self):
        product_id = self._create_sample_product(name='name1')
        self._create_sample_product_version(product_id=product_id,
                                            version="1.0")
        pv_id = self._get_product_version_id_by_version_name(product_id, "1.0")
        platform_id = self._create_sample_platform(name='plat1',
                                                   location='location1',
                                                   contact='contact1')
        status_dict = dict(platform_id=platform_id,
                           product_version_id=pv_id,
                           status=models.Status.NOT_TESTED,
                           logs_location="swift://localhost/deploy")
        self.post_json("/status", status_dict, status=201)
        self.post_json("/status", status_dict, status=409)

    def test_delete_versions_status(self):
        product_id = self._create_sample_product(name='name1')
        pv_id = self._create_sample_product_version(
            product_id=product_id, version="1.0")
        platform_id = self._create_sample_platform(
            name='plat1', location='location1', contact='contact1')

        status_dict = dict(platform_id=platform_id,
                           product_version_id=pv_id,
                           status=models.Status.NOT_TESTED,
                           logs_location="swift://localhost/deploy")
        self.post_json("/status", status_dict, status=201)
        self.delete('/status/%s/%s' % (platform_id, pv_id), status=204)

    def test_delete_versions_status_as_user(self):
        product_id = self._create_sample_product(name='name1')
        pv_id = self._create_sample_product_version(
            product_id=product_id, version="1.0")
        platform_id = self._create_sample_platform(
            name='plat1',
            location='location1',
            contact='contact1')

        status_dict = dict(platform_id=platform_id,
                           product_version_id=pv_id,
                           status=models.Status.NOT_TESTED,
                           logs_location="swift://localhost/deploy")
        self.post_json("/status", status_dict, status=201)
        self.delete('/status/%s/%s' % (platform_id, pv_id),
                    headers={'X-Auth-Token': utils.MEMBER_TOKEN},
                    status=403)

    def test_update_versions_status(self):
        product_id = self._create_sample_product(name='name1')
        pv_id = self._create_sample_product_version(
            product_id=product_id, version="1.0")
        platform_id = self._create_sample_platform(
            name='plat1', location='location1', contact='contact1')

        status_dict = dict(platform_id=platform_id,
                           product_version_id=pv_id,
                           status=models.Status.NOT_TESTED,
                           logs_location="swift://localhost/deploy")
        self.post_json("/status", status_dict, status=201)

        new_status_dict = dict(platform_id=platform_id,
                               product_version_id=pv_id,
                               status=models.Status.SUCCESS,
                               logs_location="swift://localhost/deploy")
        self.put_json("/status", new_status_dict, status=204)

    def test_update_versions_status_as_user(self):
        product_id = self._create_sample_product(name='name1')
        pv_id = self._create_sample_product_version(
            product_id=product_id, version="1.0")
        platform_id = self._create_sample_platform(
            name='plat1', location='location1', contact='contact1')

        status_dict = dict(platform_id=platform_id,
                           product_version_id=pv_id,
                           status=models.Status.NOT_TESTED,
                           logs_location="swift://localhost/deploy")
        self.post_json("/status", status_dict, status=201)

        new_status_dict = dict(platform_id=platform_id,
                               product_version_id=pv_id,
                               status=models.Status.SUCCESS,
                               logs_location="swift://localhost/deploy")
        self.put_json("/status", new_status_dict,
                      headers={'X-Auth-Token': utils.MEMBER_TOKEN},
                      status=403)

    def test_update_versions_status_not_found(self):
        platform_id = self._create_sample_platform(
            name='plat1', location='location1', contact='contact1')
        new_status_dict = dict(platform_id=platform_id,
                               product_version_id=1234,
                               status=models.Status.SUCCESS,
                               logs_location="swift://localhost/deploy")
        self.put_json("/status", new_status_dict, status=404)

    def test_get_version_status(self):
        product_id = self._create_sample_product(name='name1')
        pv_id = self._create_sample_product_version(
            product_id=product_id, version="1.0")
        platform_id = self._create_sample_platform(
            name='plat1', location='location1', contact='contact1')

        status_dict = dict(platform_id=platform_id,
                           product_version_id=pv_id,
                           status=models.Status.SUCCESS,
                           logs_location="swift://localhost/deploy")
        self.post_json("/status", status_dict, status=201)
        self.get_json("/status/%s/%s" % (platform_id, pv_id), status=200)

    def test_get_version_status_as_user(self):
        product_id = self._create_sample_product(name='name1')
        pv_id = self._create_sample_product_version(
            product_id=product_id, version="1.0")
        platform_id = self._create_sample_platform(
            name='plat1', location='location1', contact='contact1')

        status_dict = dict(platform_id=platform_id,
                           product_version_id=pv_id,
                           status=models.Status.SUCCESS,
                           logs_location="swift://localhost/deploy")
        self.post_json("/status", status_dict, status=201)
        self.get_json("/status/%s/%s" % (platform_id, pv_id),
                      headers={'X-Auth-Token': utils.MEMBER_TOKEN},
                      status=403)

    def test_get_version_status_not_found(self):
        platform_id = self._create_sample_platform(
            name='plat1', location='location1', contact='contact1')
        self.get_json("/status/%s/12345" % platform_id, status=404)

    def test_get_version_status_with_non_existing_platform(self):
        self.get_json("/status/plat1/12345", status=404)
