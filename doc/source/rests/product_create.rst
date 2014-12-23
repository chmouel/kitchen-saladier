POST /products
==============

Get saladier public URL with version and location public.

This will create a product that will be handled by a `team` with a
`contact`.

Arguments::

    {
        "contact": "blah@blah.com",
        "name": "product1",
        "team": "thebestone"
    }

Returns::

    201

.. note:: This call needs to be made with the admin rights.
