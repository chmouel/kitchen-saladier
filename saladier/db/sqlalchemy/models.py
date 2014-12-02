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
import uuid


from oslo.db.sqlalchemy import models
import sqlalchemy
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import orm


class SaladierBase(models.TimestampMixin,
                   models.ModelBase):
    def save(self, session=None):
        import saladier.db.api as db_api

        if session is None:
            session = db_api.get_session()

        super(SaladierBase, self).save(session)

Base = declarative_base(cls=SaladierBase)


class Product(Base):
    __tablename__ = "products"
    __table_args__ = {'sqlite_autoincrement': True}

    id = sqlalchemy.Column(sqlalchemy.String(36), primary_key=True,
                           default=lambda: str(uuid.uuid4()))
    name = sqlalchemy.Column(sqlalchemy.String(255), unique=True,
                             nullable=False)
    team = sqlalchemy.Column(sqlalchemy.String(255), nullable=False)
    contact = sqlalchemy.Column(sqlalchemy.String(255), nullable=False)

    def __repr__(self):
        return "<Product(name='%s', team='%s', contact='%s')>" % (
            self.name, self.team, self.contact)


class ProductVersion(Base):
    __tablename__ = "product_versions"

    id = sqlalchemy.Column(sqlalchemy.String(36), primary_key=True,
                           default=lambda: str(uuid.uuid4()))
    # TODO(Gonéri): version should be called name for consistency
    version = sqlalchemy.Column(sqlalchemy.String(255))
    product_id = sqlalchemy.Column(sqlalchemy.String(36),
                                   sqlalchemy.ForeignKey('products.id',
                                                         ondelete='cascade'))
    uri = sqlalchemy.Column(sqlalchemy.String(255))
    platforms = orm.relationship("ProductVersionStatus")

    def __repr__(self):
        return "<ProductVersion(product_id='%s', version='%s')>" % (
            self.product_id, self.version)


class Platform(Base):
    __tablename__ = "platforms"

    id = sqlalchemy.Column(sqlalchemy.String(36), primary_key=True,
                           default=lambda: str(uuid.uuid4()))
    name = sqlalchemy.Column(sqlalchemy.String(255), unique=True,
                             nullable=False)
    location = sqlalchemy.Column(sqlalchemy.String(255), nullable=False)
    contact = sqlalchemy.Column(sqlalchemy.String(255), nullable=False)

    tenant_id = sqlalchemy.Column(sqlalchemy.String(36), nullable=False)

    def __repr__(self):
        return ("<Platform(name='%s', location='%s', contact='%s', "
                "tenant_id='%s')>" % (self.name, self.location, self.contact,
                                      self.tenant_id))


class Subscriptions(Base):
    __tablename__ = "subscriptions"
    __table_args__ = (
        sqlalchemy.schema.UniqueConstraint('product_id',
                                           'tenant_id',
                                           name='uniq_tenantname@product'),
    )
    id = sqlalchemy.Column(sqlalchemy.String(36), primary_key=True,
                           default=lambda: str(uuid.uuid4()))

    tenant_id = sqlalchemy.Column(sqlalchemy.String(36), nullable=False)
    product_id = sqlalchemy.Column(sqlalchemy.String(36),
                                   sqlalchemy.ForeignKey('products.id',
                                                         ondelete='cascade'))

    def __repr__(self):
        str = "<Subscriptions(tenant_id='%s', product_id='%s')>"
        return str % (self.tenant_id, self.product_id)


class Status:
    NOT_TESTED = "NOT_TESTED"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"


class ProductVersionStatus(Base):
    __tablename__ = "product_versions_status"

    id = sqlalchemy.Column(sqlalchemy.String(36), primary_key=True,
                           default=lambda: str(uuid.uuid4()))
    product_version_id = sqlalchemy.Column(sqlalchemy.String(36),
                                           sqlalchemy.ForeignKey(
                                               'product_versions.id'))
    platform_id = sqlalchemy.Column(sqlalchemy.String(36),
                                    sqlalchemy.ForeignKey('platforms.id',
                                                          ondelete='cascade'))
    status = sqlalchemy.Column(sqlalchemy.String(255), nullable=False)
    logs_location = sqlalchemy.Column(sqlalchemy.String(255))
    platform = orm.relationship("Platform")
