GET /status/platform1/product_version_id
========================================

Show product version status

Returns::

    200

    {
        "platform_name": "platform1",
        "status": "NOT_TESTED",
        "logs_location": "swift://localhost/deploy",
        "product_version_id": "c857c729-4271-40b0-b721-28e4dbbd485d"
    }

.. note:: This call needs to be made with the admin rights.
