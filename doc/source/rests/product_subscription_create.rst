POST /subscriptions
===================

Subscribe a tenant to a product.

Arguments::

    {
        "tenant_id": "TENANT_ID",
        "product_id": "GENERATED_UUID"
    }

Returns::

    201

.. note:: This call needs to be made with the admin rights.
