PUT /status
===========

Update the status of our product version

Arguments::

    {
        "platform_name": "platform1",
        "new_logs_location": "swift://localhost/deploy_new",
        "new_status": "SUCCESS",
        "product_version_id": "c857c729-4271-40b0-b721-28e4dbbd485d"
    }

Returns::

    204

.. note:: This call needs to be made with the admin rights.
