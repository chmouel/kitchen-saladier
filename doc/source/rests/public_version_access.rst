GET /
=====

Show information about the saladier server.

.. note:: This call does not need authentication and can be used for
          healthchecking.

Returns::

    200

    {
        "version": "0.0.0.189",
        "location": "Paris",
        "provider": "eNovance"
    }

