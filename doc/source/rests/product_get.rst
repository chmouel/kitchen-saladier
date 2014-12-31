GET /products/product1
======================

Get saladier by name or id.

Get saladier product directly by name or id

Returns::

    200

    {
        "versions": [
                {
                        "url": "http://somewhereoutthere",
                        "ready_for_deploy": false,
                        "version": "1.0",
                        "id": "GENERATED_UUID",
                        "validated_on": [
                                {
                                        "status": "SUCCESS",
                                        "product_version_id": "GENERATED_UUID",
                                        "created_at": "DATETIME",
                                        "updated_at": null,
                                        "platform_id": "GENERATED_UUID",
                                        "logs_location": "swift://localhost/deploy_new",
                                        "id": "GENERATED_UUID"
                                }
                        ]
                }
        ],
        "contact": "blah@blah.com",
        "id": "GENERATED_UUID",
        "name": "product1",
        "team": "thebestone"
    }

