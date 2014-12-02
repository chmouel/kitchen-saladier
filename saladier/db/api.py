# -*- coding: utf-8 -*-
# Copyright (C) 2013 eNovance SAS <licensing@enovance.com>
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

"""SQLAlchemy storage backend."""

from oslo.config import cfg
from oslo.db import exception as db_exc
from oslo.db.sqlalchemy import session as db_session
from oslo.db.sqlalchemy import utils as db_utils

from saladier.common import exception
import saladier.db.sqlalchemy
from saladier.db.sqlalchemy import models
from saladier.openstack.common import log

CONF = cfg.CONF
LOG = log.getLogger(__name__)


_FACADE = None
_SESSION = None


def _create_facade_lazily():
    global _FACADE
    if _FACADE is None:
        _FACADE = db_session.EngineFacade.from_config(CONF)
    return _FACADE


def get_engine():
    facade = _create_facade_lazily()
    return facade.get_engine()


def get_session(**kwargs):
    """Reuse the same session so we can rollback for tests or get a new one

    This probably can get optimised.
    """
    recycle = False
    global _SESSION
    facade = _create_facade_lazily()

    if 'recycle' in kwargs:
        kwargs.pop('recycle')
        recycle = True

    session = facade.get_session(**kwargs)
    if recycle:
        _SESSION = session

    if _SESSION is not None:
        return _SESSION

    return session


def get_backend():
    """The backend is this module itself."""
    return Connection()


def model_query(model, *args, **kwargs):
    """Query helper for simpler session usage.

    :param session: if present, the session to use
    """

    session = kwargs.get('session') or get_session()
    query = session.query(model, *args)
    return query


def _paginate_query(model, limit=None, marker=None, sort_keys=None,
                    sort_dir=None, query=None):
    if type(sort_keys) is str:
        sort_keys = [sort_keys]

    if not query:
        query = model_query(model)
    query = db_utils.paginate_query(query, model, limit, sort_keys,
                                    marker=marker, sort_dir=sort_dir)
    return query.all()


def rollback():
    session = get_session()
    session.rollback()


class Connection(object):  # TODO(chmouel): base class
    """SqlAlchemy connection."""

    def create_product(self, name, team, contact):
        product = models.Product(name=name, team=team, contact=contact)

        try:
            product.save()
            return product
        except db_exc.DBDuplicateEntry:
            raise exception.ProductAlreadyExists(name)

    def delete_product(self, id):
        query = model_query(models.Product).filter(
            (models.Product.id == id) | (models.Product.name == id))
        query.delete()

    # TODO(chmou): Make those filters working (they don't do anything yet)
    def get_all_products(self, tenant_id, admin=False,
                         filters=None, limit=None,
                         marker=None, sort_key=None,
                         sort_dir=None):
        sort_key = sort_key or 'name'
        query = model_query(models.Product)
        # NOTE(chmou): This would list everthing when in admins
        if not admin:
            query = query.join(models.Subscriptions).filter(
                tenant_id == models.Subscriptions.tenant_id)
        return _paginate_query(models.Product, limit, marker,
                               sort_key, sort_dir, query)

    def get_product(self, id, tenant_id, admin=False):
        query = model_query(models.Product).filter(
            (models.Product.id == id) | (models.Product.name == id))

        if not admin:
            query = query.join(models.Subscriptions).filter(
                tenant_id == models.Subscriptions.tenant_id)
        try:
            return query.one()
        except saladier.db.sqlalchemy.exc.NoResultFound:
            raise exception.ProductNotFound(name=id)

    def create_product_version(self, product_id, version, uri):
        query = model_query(models.ProductVersion)
        if query.filter(models.Product.id == product_id).filter_by(
                version=version).all():
            raise exception.ProductVersionAlreadyExists(product_id)
        new = models.ProductVersion(version=version,
                                    product_id=product_id,
                                    uri=uri)
        new.save()
        return new

    def get_product_version_by_id(self, id, session=None):
        query = model_query(models.ProductVersion,
                            session=session).filter_by(id=id)
        try:
            return query.one()
        except saladier.db.sqlalchemy.exc.NoResultFound:
            raise exception.ProductVersionNotFound(name=id)

    def get_all_product_versions(self, product_id):
        query = model_query(models.ProductVersion)
        res = query.filter(models.Product.id == product_id).all()
        # TODO(chmou): filtering/paging and such
        return res

    def delete_product_versions(self, product_id, version):
        query = model_query(models.ProductVersion).filter_by(
            product_id=product_id, version=version)
        query.delete()

    def create_platform(self, name, location, contact, tenant_id):
        platform = models.Platform(name=name, location=location,
                                   contact=contact, tenant_id=tenant_id)

        try:
            platform.save()
            return platform
        except db_exc.DBDuplicateEntry:
            raise exception.PlatformAlreadyExists(name)

    def delete_platform(self, id):
        query = model_query(models.Platform).filter(
            (models.Platform.id == id) | (models.Platform.name == id))
        query.delete()

    def get_all_platforms(self, filters=None, limit=None, marker=None,
                          sort_key=None, sort_dir=None):
        sort_key = sort_key or 'name'
        query = model_query(models.Platform)
        return _paginate_query(models.Platform, limit, marker,
                               sort_key, sort_dir, query)

    def get_platform(self, id):
        query = model_query(models.Platform).filter(
            (models.Platform.id == id) | (models.Platform.name == id))
        try:
            return query.one()
        except saladier.db.sqlalchemy.exc.NoResultFound:
            raise exception.PlatformNotFound(name=id)

    # -*- Subscriptions -*-
    def create_subscription(self, tenant_id, product_id):
        query = models.Subscriptions(tenant_id=tenant_id,
                                     product_id=product_id)
        try:
            query.save()
        except db_exc.DBDuplicateEntry:
            raise exception.SubscriptionAlreadyExists(product_id)

    def delete_subscription(self, product_id, tenant_id):
        model = (model_query(models.Subscriptions).
                 filter_by(product_id=product_id).
                 filter_by(tenant_id=tenant_id))
        model.delete()

    def get_subscriptions_for_tenant_id(self, tenant_id):
        query = model_query(models.Subscriptions).filter_by(
            tenant_id=tenant_id)
        return query.all()

    def add_version_status(self, platform_id, product_version_id, status,
                           logs_location):
        versions_status = (model_query(models.ProductVersionStatus).
                           filter_by(platform_id=platform_id).
                           filter_by(product_version_id=product_version_id).
                           first())

        if versions_status:
            raise exception.ProductVersionStatusAlreadyExists(
                "%s,%s" % (platform_id, product_version_id))

        session = get_session()
        with session.begin(subtransactions=True):
            platform = self.get_platform(platform_id)
            product_version = self.get_product_version_by_id(
                product_version_id, session=session)
            product_version_status = models.ProductVersionStatus(
                status=status, logs_location=logs_location)
            product_version_status.platform = platform
            product_version.platforms.append(product_version_status)
            try:
                product_version.save(session)
            except exception.SaladierFlushError:
                # NOTE(Gonéri): I think this should never happend
                raise exception.ProductVersionStatusAlreadyExists(
                    name="%s, %s" % (platform_id, product_version_id))

    def get_version_status(self, platform_id, product_version_id):
        query = model_query(models.ProductVersionStatus)
        try:
            return query.filter_by(platform_id=platform_id,
                                   product_version_id=product_version_id).one()
        except saladier.db.sqlalchemy.exc.NoResultFound:
            raise exception.ProductVersionStatusNotFound(
                "name=%s,%s" % (platform_id, product_version_id))

    def get_all_status_by_version_id(self, product_version_id):
        query = model_query(models.ProductVersionStatus)
        try:
            return query.filter_by(product_version_id=product_version_id).all()
        except saladier.db.sqlalchemy.exc.NoResultFound:
            raise exception.ProductVersionStatusNotFound(id=product_version_id)

    def get_all_versions_status(self):
        return model_query(models.ProductVersionStatus).all()

    def update_version_status(self, platform_id, product_version_id,
                              status, logs_location):

        product_version_status = self.get_version_status(platform_id,
                                                         product_version_id)
        product_version_status.status = status
        product_version_status.logs_location = logs_location
        product_version_status.save()

    def delete_version_status(self, platform_id, product_version_id):
        query = model_query(models.ProductVersionStatus).filter_by(
            platform_id=platform_id, product_version_id=product_version_id)
        query.delete()
