POST /status
============

Add a status to a product version.

Status can be of ('NOT_TESTED', 'SUCCESS', 'FAILED')

Arguments::

    {
        "platform_id": "GENERATED_UUID",
        "status": "SUCCESS",
        "logs_location": "swift://localhost/deploy_new",
        "product_version_id": "GENERATED_UUID"
    }

Returns::

    201

