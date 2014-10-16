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

    def get_product_by_name(self, session, name):
        """Retrieve a product by giving its name.

        :param session: the session to use for the query
        :param name: the product name to query for
        """

        product = session.query(models.Product).filter_by(name=name).one()
        return product

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
        product = self.get_product_by_name(session, current_name)
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

    def get_products(self, session):
        """Get all the products from the database.

        :param session: the session to use for the query
        """
        all_products = []
        for p in session.query(models.Product).order_by(models.Product.id):
            all_products.append({"name": p.name, "team": p.team,
                                 "contact": p.contact})
        return {"products": all_products}

    # CRUD product versions
    def create_product_version(self, session, product_id, version):
        product_version = models.ProductVersion(product_id=product_id,
                                                version=version)
        self._add_and_flush(session, product_version)

    def create_customer(self, session, name):
        customer = models.Customer(name=name)
        self._add_and_flush(session, customer)

    def create_platform(self, session, location, email, customer_id):
        platform = models.Platform(location=location, email=email,
                                   customer_id=customer_id)
        self._add_and_flush(session, platform)

    def create_access(self, session, url, ssh_key, username, password,
                      platform_id):
        access = models.Access(url=url, ssh_key=ssh_key, username=username,
                               password=password, platform_id=platform_id)
        self._add_and_flush(session, access)
