===
API
===

The `Saladier` provide a simple REST API for querying or setting infos
about products.

The authentication to the API is based like a standard `OpenStack`
service where you receive a token from `Keystone` and pass that token
to the `Saladier` within the ``X-Auth-Token`` header.

The ACL and RBAC rights is managed by `Keystone policies`_ and handled
directly by the same engine there.

HTTP Status Codes
=================

The Saladier API uses a subset of the available HTTP status codes to
communicate specific success and failure conditions to the client.

200 OK
------

This status code is returned in response to successful `GET` and `PATCH`
operations.

201 Created
-----------

This status code is returned in response to successful `POST` operations.

204 No Content
--------------

This status code is returned in response to successful `HEAD`, `PUT` and
`DELETE` operations.

400 Bad Request
---------------

This status code is returned when the Saladier fails to parse the
request as expected. This is most frequently returned when a required attribute
is missing, a disallowed attribute is specified (such as an `id` on `POST` in a
basic CRUD operation), or an attribute is provided of an unexpected data type.

The client is assumed to be in error.

401 Unauthorized
----------------

This status code is returned when either authentication has not been performed,
the provided X-Auth-Token is invalid or authentication credentials are invalid
(including the user, project or domain having been disabled).

403 Forbidden
-------------

This status code is returned when the request is successfully authenticated but
not authorized to perform the requested action.

404 Not Found
-------------

This status code is returned in response to failed `GET`, `HEAD`, `POST`,
`PUT`, `PATCH` and `DELETE` operations when a referenced entity cannot be found
by ID. In the case of a `POST` request, the referenced entity may be in the
request body as opposed to the resource path.

409 Conflict
------------

This status code is returned in response to failed `POST` and `PATCH`
operations. For example, when a client attempts to update an entity's unique
attribute which conflicts with that of another entity in the same collection.

Alternatively, a client should expect this status code when attempting to
perform the same create operation twice in a row on a collection with a
user-defined and unique attribute. For example, a User's `name` attribute is
defined to be unique and user-defined, so making the same ``POST /users``
request twice in a row will result in this status code.

The client is assumed to be in error.

500 Internal Server Error
-------------------------

This status code is returned when an unexpected error has occurred in the
Saladier service implementation.

501 Not Implemented
-------------------

This status code is returned when the Saladier service implementation is unable
to fulfill the request because it is incapable of implementing the entire API
as specified.

For example, an Saladier service may be incapable of returning an exhaustive
collection of Products with any reasonable expectation of performance, or lack
the necessary permission to create or modify the collection of users (which may
be managed by a remote system); the implementation may therefore choose to
return this status code to communicate this condition to the client.

503 Service Unavailable
-----------------------

This status code is returned when the Saladier service is unable to communicate
with a backend service, or by a proxy in front of the Saladier service unable
to communicate with the Saladier service itself.

.. include:: rests/public_version_access.rst

.. include:: rests/product_create.rst

.. include:: rests/product_list.rst

.. include:: rests/product_get.rst

.. include:: rests/product_get_version.rst

.. include:: rests/product_delete.rst

.. include:: rests/product_subscription_create.rst

.. include:: rests/product_subscription_delete.rst

.. include:: rests/product_version_create.rst

.. include:: rests/product_version_delete.rst

.. include:: rests/platform_create.rst

.. include:: rests/platform_list.rst

.. include:: rests/platform_delete.rst

.. include:: rests/product_version_status_add.rst

.. include:: rests/product_version_status_delete.rst

.. include:: rests/product_version_status_show.rst

.. include:: rests/product_version_status_update.rst

.. _`Keystone policies`: https://access.redhat.com/documentation/en-US/Red_Hat_Enterprise_Linux_OpenStack_Platform/4/html/Configuration_Reference_Guide/ch_configuring-openstack-identity.html#section_keystone-policy.json
