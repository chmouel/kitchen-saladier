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
                                        "ready_for_deploy": false,
                                        "version": "1.0",
                                        "id": "badde9a4-d86e-442a-9d4a-8686c65036ec",
                                        "validated_on": [
                                                {
                                                        "status": "SUCCESS",
                                                        "product_version_id": "badde9a4-d86e-442a-9d4a-8686c65036ec",
                                                        "created_at": "2014-12-18 15:47:27",
                                                        "updated_at": null,
                                                        "platform_id": "8b903162-97cf-4ec3-83e2-e719ff604afa",
                                                        "logs_location": "swift://localhost/deploy_new",
                                                        "id": "093076d6-c53d-4e99-a15c-ee8330132e29"
                                                }
                                        ],
                                        "uri": "http://somewhereoutthere"
                                }
                        ],
                        "contact": "blah@blah.com",
                        "id": "d6c308c9-20bd-4160-bf62-041b7031187c",
                        "name": "product1",
                        "team": "thebestone"
                }
        ]
    }

