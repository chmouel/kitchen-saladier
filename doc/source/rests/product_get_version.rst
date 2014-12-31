GET /products/product_name_or_id/version_name_or_id
===================================================

Show specific product/version information.

Returns::

    200

    {
        "url": "http://somewhereoutthere",
        "ready_for_deploy": false,
        "version": "1.0",
        "id": "GENERATED_UUID",
        "validated_on": []
    }

.. note:: This call needs to be made with the admin rights.
