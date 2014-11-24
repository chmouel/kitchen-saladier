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
import saladier.api.controllers.v1.platforms as platform_controller
import saladier.api.controllers.v1.product_versions as product_versions
import saladier.api.controllers.v1.products as product_controller
import saladier.api.controllers.v1.subscriptions as subscriptions
from saladier.openstack.common import log

LOG = log.getLogger(__name__)


class V1Controller(object):
    """Version 1 API controller root."""

    products = product_controller.ProductController()
    platforms = platform_controller.PlatformController()
    versions = product_versions.ProductVersionsController()
    subscriptions = subscriptions.SubscriptionController()
