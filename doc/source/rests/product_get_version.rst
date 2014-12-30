GET /products/product_name_or_id/version_name_or_id
===================================================

Show specific product/version information.

Returns::

    200

    {
        "ready_for_deploy": false,
        "version": "1.0",
        "id": "badde9a4-d86e-442a-9d4a-8686c65036ec",
        "validated_on": [],
        "uri": "http://somewhereoutthere"
    }

.. note:: This call needs to be made with the admin rights.
