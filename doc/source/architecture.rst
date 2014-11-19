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

==========
Data model
==========

The data model of the Control server is described below:

.. graphviz::

   digraph structs {
     node [shape=plaintext]

       SUBSCRIPTIONS [label=<
       <table border="0" cellborder="1" cellspacing="0" align="left">
       <tr><td BGCOLOR="Lavender">SUBSCRIPTIONS</td></tr>
       <tr><td PORT="TENANT_ID">Tenant ID</td></tr>
       <tr><td PORT="PRODUCT_ID">Product ID</td></tr>
       </table>>];

       PRODUCTS [label=<
       <table border="0" cellborder="1" cellspacing="0" align="left">
       <tr><td BGCOLOR="Lavender">PRODUCTS</td></tr>
       <tr><td PORT="PRODUCT_ID">Product ID</td></tr>
       <tr><td PORT="Name">Name</td></tr>
       <tr><td PORT="Team">Team</td></tr>
       <tr><td PORT="Contact_email">Contact email</td></tr>
       </table>>];

       PRODUCT_VERSIONS_STATUS [label=<
       <table border="0" cellborder="1" cellspacing="0" align="left">
       <tr><td BGCOLOR="Lavender">PRODUCT_VERSIONS_STATUS </td></tr>
       <tr><td PORT="Platform_NAME">Platform name</td></tr>
       <tr><td PORT="PRODUCT_VERSION_ID">Product version ID</td></tr>
       <tr><td PORT="STATUS">Status</td></tr>
       <tr><td PORT="LOGS_LOCATION">Logs location</td></tr>
       </table>>];

       PLATFORMS [label=<
       <table border="0" cellborder="1" cellspacing="0" align="left">
       <tr><td BGCOLOR="Lavender">PLATFORMS</td></tr>
       <tr><td PORT="PLATFORM_NAME">Platform name</td></tr>
       <tr><td PORT="Tenant_ID">Tenant ID</td></tr>
       <tr><td PORT="Location">Location</td></tr>
       <tr><td PORT="Notes">Contact email</td></tr>
       </table>>];

       PRODUCT_VERSIONS [label=<
       <table border="0" cellborder="1" cellspacing="0" align="left">
       <tr><td BGCOLOR="Lavender">PRODUCT_VERSIONS</td></tr>
       <tr><td PORT="PRODUCT_VERSION_ID">Product version ID</td></tr>
       <tr><td PORT="Product_ID">Product ID</td></tr>
       <tr><td PORT="Version">Version</td></tr>
       <tr><td PORT="Uri">Uri</td></tr>
       </table>>];

       ACCESS [label=<
       <table border="0" cellborder="1" cellspacing="0" align="left">
       <tr><td BGCOLOR="Lavender">ACCESS</td></tr>
       <tr><td PORT="Platform_NAME">Platform name</td></tr>
       <tr><td PORT="Url">Url</td></tr>
       <tr><td PORT="SSH Key">SSH Key</td></tr>
       <tr><td PORT="Username">Username</td></tr>
       <tr><td PORT="Password">Password</td></tr>
       </table>>];

       SUBSCRIPTIONS:PRODUCT_ID -> PRODUCTS:PRODUCT_ID[label = "N .. N"];
       PRODUCT_VERSIONS_STATUS:PLATFORM_NAME -> PLATFORMS:PLATFORM_NAME[label = "N .. N"];
       PRODUCT_VERSIONS_STATUS:PRODUCT_VERSION_ID -> PRODUCT_VERSIONS:PRODUCT_VERSION_ID[label = "N .. N"];
       ACCESS:Platform_ID -> PLATFORMS:PLATFORM_NAME[label = "N .. 1"];
       PRODUCT_VERSIONS:Product_ID -> PRODUCTS:PRODUCT_ID[label = "N .. 1"];
   }
