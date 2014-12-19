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
from saladier_integrationtests.restgen import base as b
import saladierclient.tests.v1.fakes as f


# Public
class PublicInformation(b.Base):
    """Show information about the saladier server.

    .. note:: This call does not need authentication and can be used for
              healthchecking.
    """
    method = "GET"
    url = "/"
    admin = False
    documentation_type = "public_version_access"


# Products
class ProductCreate(b.Base):
    """Get saladier public URL with version and location public.

    This will create a product that will be handled by a `team` with a
    `contact`.
    """
    method = "POST"
    url = "products"
    admin = True
    documentation_type = "product_create"
    data = f.CREATE_PRODUCT


class ProductShow(b.Base):
    """Get saladier by name or id.

    Get saladier product directly by name or id
    """
    method = "GET"
    url = "products/" + f.CREATE_PRODUCT['name']
    documentation_type = "product_get"
    admin = False


class ProductShowVersion(b.Base):
    """Show specific product/version information."""
    method = "GET"
    base_url = "products"
    url = base_url + "/product_name_or_id/version_name_or_id"
    documentation_type = "product_get_version"
    admin = True


class ProductList(b.Base):
    """List available products for the current users."""
    admin = False
    method = "GET"
    url = "products"
    documentation_type = "product_list"


class ProductDelete(b.Base):
    """Delete Product.

    Make sure all the associations to the product is already deleted before
    doing this operation or this will conflict.
    """
    method = "DELETE"
    base_url = "products"
    url = base_url + "/product_name_or_id"
    admin = True
    documentation_type = "product_delete"


# Versions
class ProductVersionCreate(b.Base):
    """Associate a product to a version."""
    method = "POST"
    url = "versions"
    admin = True
    data = f.CREATE_PRODUCT_VERSIONS
    documentation_type = "product_version_create"


class ProductVersionDelete(b.Base):
    """Delete an association between a product to a version."""
    method = "DELETE"
    base_url = "versions"
    url = base_url + "/product_name_or_id/version_name_or_id"
    admin = True
    documentation_type = "product_version_delete"


# Platforms
class PlatformCreate(b.Base):
    """Create Platform."""
    method = "POST"
    url = "platforms"
    admin = True
    data = f.CREATE_PLATFORM
    documentation_type = "platform_create"


class PlatformList(b.Base):
    """List Platforms."""
    method = "GET"
    url = "platforms"
    admin = False
    documentation_type = "platform_list"


class PlatformDelete(b.Base):
    """Delete a platform."""
    base_url = "platforms"
    url = base_url + "/platform_id"
    method = "DELETE"
    admin = True
    documentation_type = "platform_delete"


# Subscription
class SubscribtionCreate(b.Base):
    """Subscribe a tenant to a product."""
    admin = True
    method = "POST"
    data = f.CREATE_SUBSCRIPTION
    documentation_type = "product_subscription_create"
    url = "subscriptions"


class SubscriptionDelete(b.Base):
    """Delete a subscription of a tenant to a product."""
    method = "DELETE"
    base_url = "subscriptions"
    url = base_url + "/product_name_or_id/tenant_id"
    admin = True
    documentation_type = "product_subscription_delete"


# Status
class StatusAdd(b.Base):
    """Add a status to a product version.

    Status can be of ('NOT_TESTED', 'SUCCESS', 'FAILED')
    """
    admin = False
    method = "POST"
    data = f.CREATE_STATUS_PRODUCT1
    url = "status"
    documentation_type = "product_version_status_add"


class StatusShow(b.Base):
    """Show a platform."""
    method = "GET"
    base_url = "status"
    url = base_url + "/PLATFORM_ID/PRODUCT_VERSION_ID"
    admin = False
    documentation_type = "product_version_status_show"


class StatusUpdate(b.Base):
    """Update a status."""
    method = "PUT"
    url = "status"
    admin = False
    documentation_type = "product_version_status_update"
    data = f.CREATE_STATUS_PRODUCT1


class StatusDelete(b.Base):
    """Delete a status."""
    method = "DELETE"
    base_url = 'status'
    url = base_url + "/PLATFORM_ID/PRODUCT_VERSION_ID"
    admin = False
    documentation_type = "product_version_status_delete"
