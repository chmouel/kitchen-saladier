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

from oslo.db.sqlalchemy import models
import sqlalchemy
from sqlalchemy.ext.declarative import declarative_base


class SaladierBase(models.TimestampMixin,
                   models.ModelBase):
    def save(self, session=None):
        import saladier.db.api as db_api

        if session is None:
            session = db_api.get_session()

        super(SaladierBase, self).save(session)

BASE = declarative_base(cls=SaladierBase)


class Product(BASE):
    __tablename__ = "products"

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    name = sqlalchemy.Column(sqlalchemy.String(255), unique=True,
                             nullable=False, primary_key=True)
    team = sqlalchemy.Column(sqlalchemy.String(255), nullable=False)
    contact = sqlalchemy.Column(sqlalchemy.String(255), nullable=False)

    def __repr__(self):
        return "<Product(name='%s', team='%s', contact='%s')>" % (
            self.name, self.team, self.contact)


class ProductVersion(BASE):
    __tablename__ = "product_versions"

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    version = sqlalchemy.Column(sqlalchemy.String(255))
    product_name = sqlalchemy.Column(sqlalchemy.String(255),
                                     sqlalchemy.ForeignKey('products.name'))
    uri = sqlalchemy.Column(sqlalchemy.String(255))

    def __repr__(self):
        return "<ProductVersion(product_name='%s', version='%s')>" % (
            self.product_name, self.version)


class Customer(BASE):
    __tablename__ = "customers"

    name = sqlalchemy.Column(sqlalchemy.String(255), unique=True,
                             nullable=False, primary_key=True)
    contact = sqlalchemy.Column(sqlalchemy.String(255))

    def __repr__(self):
        return "<Customer(name='%s')>" % self.name


class Platform(BASE):
    __tablename__ = "platforms"

    name = sqlalchemy.Column(sqlalchemy.String(255), unique=True,
                             nullable=False, primary_key=True)
    location = sqlalchemy.Column(sqlalchemy.String(255))
    contact = sqlalchemy.Column(sqlalchemy.String(255))

    customer_name = sqlalchemy.Column(sqlalchemy.String(255),
                                      sqlalchemy.ForeignKey('customers.name'))

    def __repr__(self):
        return "<Platform(location='%s', email='%s', customer_id='%s')>" % (
            self.location, self.email, self.customer_id)


class Access(BASE):
    __tablename__ = "accesses"

    username = sqlalchemy.Column(sqlalchemy.String(255), unique=True,
                                 nullable=False, primary_key=True)
    password = sqlalchemy.Column(sqlalchemy.String(255))

    url = sqlalchemy.Column(sqlalchemy.String(255))
    ssh_key = sqlalchemy.Column(sqlalchemy.String(255))
    platform_name = sqlalchemy.Column(sqlalchemy.String(255),
                                      sqlalchemy.ForeignKey('platforms.name'))
