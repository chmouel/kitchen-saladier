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

from oslo.db.sqlalchemy import session as db_session


class DbApi(object):

    def __init__(self, conf):
        self.conf = conf
        self._engine_facade = None

    def connect(self):
        self._engine_facade = db_session.EngineFacade.from_config(self.conf)
        try:
            models.BASE.metadata.create_all(self._engine_facade.get_engine())
        except Exception:
            pass

    def disconnect(self):
        self._engine_facade.get_engine().dispose()

    def _add_and_commit(self, ki_object):
        session = self._engine_facade.get_session()
        with session.begin():
            session.add(ki_object)

    # CRUD Products
    def create_product(self, name, team, contact):
        product = models.Product(name=name, team=team, contact=contact)
        self._add_and_commit(product)

    def get_product_by_name(self, name):
        session = self._engine_facade.get_session()
        product = session.query(models.Product).filter_by(name=name).one()
        return product

    def update_product(self, current_name, new_name=None, new_team=None,
                       new_contact=None):
        product = self.get_product_by_name(current_name)
        if new_name:
            product.name = new_name
        if new_team:
            product.team = new_team
        if new_contact:
            product.contact = new_contact
        self._add_and_commit(product)

    def delete_product(self, name):
        session = self._engine_facade.get_session()
        session.query(models.Product).filter_by(name=name).delete()

    def get_products(self):
        session = self._engine_facade.get_session()
        all_products = []
        for p in session.query(models.Product).order_by(models.Product.id):
            all_products.append({"name": p.name, "team": p.team,
                                 "contact": p.contact})
        return {"products": all_products}

    # CRUD product versions
    def create_product_version(self, product_id, version):
        product_version = models.ProductVersion(product_id=product_id,
                                                version=version)
        self._add_and_commit(product_version)

    def create_customer(self, name):
        customer = models.Customer(name=name)
        self._add_and_commit(customer)

    def create_platform(self, location, email, customer_id):
        platform = models.Platform(location=location, email=email,
                                   customer_id=customer_id)
        self._add_and_commit(platform)

    def create_access(self, url, ssh_key, username, password, platform_id):
        access = models.Access(url=url, ssh_key=ssh_key, username=username,
                               password=password, platform_id=platform_id)
        self._add_and_commit(access)
