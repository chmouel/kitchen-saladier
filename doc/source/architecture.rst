============
Architecture
============

The Saladier sits right in the middle at the Service Provider premises
(i.e: eNovance, Red Hat) along the Product Server,

::

                     +-------+
                     |       |
                     |Product|
                     |       |
                     +---+---+
                         |
                         |
                   +-----+-----+
                   |           |
                   |           |
                   |  Saladier |
                   |           |
                   |           |
                   |           |
                  XX-----X-----XX
                XXX      X       XXX
              XXX        X          XXX
    +-----------+    +--------+   +------------+
    |           |    |        |   |            |
    | Jenkins1  |    |Jenkins2|   | Jenkins3   |
    |           |    |        |   |            |
    |           |    |        |   |            |
    +-----------+    +--------+   +------------+

==========
 Workflow
==========

Take for example when you have a product named `product-1.0` the
product being subscribed to by the customer. This information being
referenced inside the `product server` with the ACL that goes along with
it.

The `ACL` is currently simply based on IPs from where the Jenkins is
coming from, in the future we can extend with Username/Password stored
in a Keystone or even better SASL type authentication.

The `Jenkins1` server has a jenkins job setup to go check what products
it can have access to and connect via API to the `saladier` to get the
list of product.

By a mean of a reference from the product server the `saladier`
will pass the product to the `Jenkins1` from a remote store
(`OpenStack Swift` etc..) in a pull based flow `Jenkins1` pulling the
product from the `saladier`.

`Jenkins1` will store that product in its own remote store and add a
job in its own Jenkins to create a test deployment job.

When the product is validated on the local CI, `Jenkins1` will
communicate the validation and time back to the `saladier` with the
deployment logs.

Assuming the same scenario with different `Jenkins` a product can end
up having multiple validation and when the product has been validated
at least a certain amount of times (TBD at product configuration
setup) it could notified the Operation team that operate the customers
of the Jenkins.
