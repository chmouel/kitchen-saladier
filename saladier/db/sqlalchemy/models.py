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
from sqlalchemy.ext import declarative
from sqlalchemy import orm


BASE = declarative.declarative_base()


class Product(BASE, models.ModelBase):
    __tablename__ = "products"

    id = sqlalchemy.Column(sqlalchemy.Integer, nullable=False,
                           primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String(255), unique=True,
                             nullable=False)
    team = sqlalchemy.Column(sqlalchemy.String(255), nullable=False)
    contact = sqlalchemy.Column(sqlalchemy.String(255), nullable=False)

    def __repr__(self):
        return "<Product(name='%s', team='%s', contact='%s')>" % (
            self.name, self.team, self.contact)


class ProductVersion(BASE, models.ModelBase):
    __tablename__ = "product_versions"

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    version = sqlalchemy.Column(sqlalchemy.String(255))
    product_id = sqlalchemy.Column(sqlalchemy.Integer,
                                   sqlalchemy.ForeignKey('products.id'))

    product = orm.relationship("Product", backref=orm.backref(
        'product_versions', order_by=id))

    def __repr__(self):
        return "<ProductVersion(product_id='%s', version='%s')>" % (
            self.product_id, self.version)


class Customer(BASE, models.ModelBase):
    __tablename__ = "customers"

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    name = sqlalchemy.Column(sqlalchemy.String(255))

    def __repr__(self):
        return "<Customer(name='%s')>" % self.name


class Platform(BASE, models.ModelBase):
    __tablename__ = "platforms"

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    location = sqlalchemy.Column(sqlalchemy.String(255))
    email = sqlalchemy.Column(sqlalchemy.String(255))

    customer_id = sqlalchemy.Column(sqlalchemy.Integer,
                                    sqlalchemy.ForeignKey('customers.id'))
    customer = orm.relationship("Customer", backref=orm.backref('platforms',
                                                                order_by=id))

    def __repr__(self):
        return "<Platform(location='%s', email='%s', customer_id='%s')>" % (
            self.location, self.email, self.customer_id)


class Access(BASE, models.ModelBase):
    __tablename__ = "accesses"

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    url = sqlalchemy.Column(sqlalchemy.String(255))
    # TODO(yassine): ssh key does not fit in String(255)
    ssh_key = sqlalchemy.Column(sqlalchemy.String(255))
    username = sqlalchemy.Column(sqlalchemy.String(255))
    password = sqlalchemy.Column(sqlalchemy.String(255))
    platform_id = sqlalchemy.Column(sqlalchemy.Integer,
                                    sqlalchemy.ForeignKey('platforms.id'))

    platform = orm.relationship("Platform", backref=orm.backref('Access ',
                                                                order_by=id))
