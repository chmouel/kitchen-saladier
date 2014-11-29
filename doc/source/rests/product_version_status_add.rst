POST /status
============

Add a status to a product version

Arguments::

    {
        "status": "NOT_TESTED",
        "platform_name": "platform1",
        "logs_location": "swift://localhost/deploy",
        "product_version_id": "c857c729-4271-40b0-b721-28e4dbbd485d"
    }

Returns::

    201

.. note:: This call needs to be made with the admin rights.
