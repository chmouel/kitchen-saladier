# -*- coding: utf-8 -*-
#
# Copyright 2014 eNovance SAS <licensing@enovance.com>
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from __future__ import absolute_import

from saladier.db.sqlalchemy import models
from saladier.openstack.common import log

from oslo.db.sqlalchemy import session as db_session

LOG = log.getLogger(__name__)


class DbApi(object):
    """This class implements the database access.

    Each call accept a session in parameters.

    Example:

    >>> db_api = DbApi(conf)
    >>> db_api.connect()
    >>> session = db_api.get_session()
    >>> session.begin()
    >>> db_api.create_product(session, name="n", team="t", contact="c")
    >>> session.commit()
    >>> session.close()
    >>> db_api.disconnect()
    """

    def __init__(self, conf):
        self.conf = conf
        self._engine_facade = None

    def connect(self):
        if not self._engine_facade:
            self._engine_facade = db_session.EngineFacade.from_config(
                self.conf)

    def disconnect(self):
        if self._engine_facade:
            self._engine_facade.get_engine().dispose()
            self._engine_facade = None

    def get_session(self):
        """Retrieve a new session."""
        if self._engine_facade:
            return self._engine_facade.get_session()
        else:
            None

    @staticmethod
    def _add_and_flush(session, ki_object):
        """Add an object into the session and flush it to the database.

        :param session: the session to use for the transaction
        :param ki_object: the object to be flushed
        """

        session.add(ki_object)
        session.flush()

    def create_product(self, session, name, team, contact):
        """Create a product and flush it through the transaction.

        :param session: the session to use for the transaction
        :param name: the product name
        :param team: the team in charge of that product
        :param contact: the address mail of the team
        """
        product = models.Product(name=name, team=team, contact=contact)
        self._add_and_flush(session, product)

    def _get_product_by_name(self, session, name):
        return session.query(models.Product).filter_by(name=name).one()

    def get_product_by_name(self, session, name):
        """Retrieve a product by giving its name.

        :param session: the session to use for the query
        :param name: the product name to query for
        """

        product = self._get_product_by_name(session, name)
        return {"name": product.name, "team": product.team,
                "contact": product.contact}

    def get_all_versions_of_product(self, session, name):
        """Retrieve all available version of a product by name.

        :param session: the session to use for the query
        :param name: the product name to query for
        """

        all_versions = session.query(models.ProductVersion).join(
            models.Product).filter(models.Product.name == name).all()

        return [version.version for version in all_versions]

    def update_product(self, session, current_name, new_name=None,
                       new_team=None, new_contact=None):
        """Update the fields of an existing product.

        All parameters are optional.

        :param session: the session to use for the transaction
        :param current_name: the current name of the product
        :param new_name: the new product name
        :param new_team: the new team
        :param new_contact: the new contact
        """
        product = self._get_product_by_name(session, current_name)
        if new_name:
            product.name = new_name
        if new_team:
            product.team = new_team
        if new_contact:
            product.contact = new_contact
        self._add_and_flush(session, product)

    def delete_product(self, session, name):
        """Delete a product.

        :param session: the session to use for the transaction
        :param name: the product name
        """
        session.query(models.Product).filter_by(name=name).delete()

    def get_all_products(self, session):
        """Get all the products from the database.

        :param session: the session to use for the query
        """
        all_products = []
        for p in session.query(models.Product):
            all_products.append({"name": p.name, "team": p.team,
                                 "contact": p.contact})
        return {"products": all_products}

    def create_product_version(self, session, product_name, version):
        product_version = models.ProductVersion(product_name=product_name,
                                                version=version)
        self._add_and_flush(session, product_version)

    def create_customer(self, session, name, contact):
        customer = models.Customer(name=name, contact=contact)
        self._add_and_flush(session, customer)

    def get_customer_by_name(self, session, name):
        """Retrieve a customer by giving its name.

        :param session: the session to use for the query
        :param name: the customer name to query for
        """

        customer = session.query(models.Customer).filter_by(name=name).one()
        return {"name": customer.name, "contact": customer.contact}

    def get_all_customers(self, session):
        """Get all the customers from the database.

        :param session: the session to use for the query
        """
        all_customers = []
        for c in session.query(models.Customer):
            all_customers.append({"name": c.name, "contact": c.contact})
        return {"customers": all_customers}

    def create_platform(self, session, name, location, contact, customer_name):
        platform = models.Platform(name=name, location=location,
                                   contact=contact,
                                   customer_name=customer_name)
        self._add_and_flush(session, platform)

    def get_platform_by_name(self, session, name):
        """Retrieve a platform by giving its name.

        :param session: the session to use for the query
        :param name: the platform name to query for
        """

        platform = session.query(models.Platform).filter_by(name=name).one()
        return {"platform": platform.name, "contact": platform.contact,
                "location": platform.location,
                "customer": platform.customer_name}

    def get_platforms_by_customer(self, session, customer_name):
        """Retrieve all platforms of a customer.

        :param session: the session to use for the query
        :param customer_name: the customer name
        """

        all_platforms = session.query(models.Platform).join(
            models.Customer).filter(
                models.Customer.name == customer_name).all()

        ret_all_platforms = []
        for platform in all_platforms:
            ret_all_platforms.append({"location": platform.location,
                                      "contact": platform.contact})
        return ret_all_platforms

    def get_all_platforms(self, session):
        """Get all the platforms from the database.

        :param session: the session to use for the query
        """
        all_platforms = []
        for p in session.query(models.Platform):
            all_platforms.append({"location": p.location,
                                  "contact": p.contact,
                                  "customer": p.customer_name})
        return {"platforms": all_platforms}

    def create_access(self, session, username, password, url, ssh_key,
                      platform_name):
        access = models.Access(username=username, password=password, url=url,
                               ssh_key=ssh_key, platform_name=platform_name)
        self._add_and_flush(session, access)

    def _get_access_by_username(self, session, username):
        return session.query(models.Access).filter_by(username=username).one()

    def get_access_by_username(self, session, username):
        """Retrieve credentials by giving the username.

        :param session: the session to use for the query
        :param username: the username to query for
        """

        access = self._get_access_by_username(session, username)
        return {"username": access.username, "password": access.password,
                "url": access.url, "ssh_key": access.ssh_key,
                "platform": access.platform_name}

    def update_access(self, session, current_username, new_username=None,
                      new_password=None, new_url=None, new_ssh_key=None,
                      new_platform_name=None):
        """Update the fields of an existing access.

        All parameters are optional.

        :param session:
        :param current_username:
        :param new_username:
        :param new_password:
        :param new_url:
        :param new_ssh_key:
        :param new_platform_name:
        :return:
        """

        access = self._get_access_by_username(session, current_username)
        if new_username:
            access.username = new_username
        if new_password:
            access.password = new_password
        if new_url:
            access.url = new_url
        if new_ssh_key:
            access.ssh_key = new_ssh_key
        if new_platform_name:
            access.platform_name = new_platform_name

        self._add_and_flush(session, access)

    def delete_access(self, session, username):
        """Delete an access.

        :param session: the session to use for the transaction
        :param username: the username access
        """
        session.query(models.Access).filter_by(username=username).delete()
