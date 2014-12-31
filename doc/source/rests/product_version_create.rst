POST /versions
==============

Associate a product to a version.

Arguments::

    {
        "url": "http://somewhereoutthere",
        "version": "1.0",
        "product_id": "GENERATED_UUID"
    }

Returns::

    201

.. note:: This call needs to be made with the admin rights.
