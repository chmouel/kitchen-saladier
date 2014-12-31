GET /products
=============

List available products for the current users.

Returns::

    200

    {
        "products": [
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
        ]
    }

