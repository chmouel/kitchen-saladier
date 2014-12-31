PUT /status
===========

Update a status.

Arguments::

    {
        "platform_id": "GENERATED_UUID",
        "status": "SUCCESS",
        "logs_location": "swift://localhost/deploy_new",
        "product_version_id": "GENERATED_UUID"
    }

Returns::

    204

