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
    facade = _create_facade_lazily()
    return facade.get_session(**kwargs)


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
        except db_exc.DBDuplicateEntry:
            raise exception.ProductAlreadyExists(name)

    def delete_product_by_name(self, name):
        # TODO(chmouel): Check that product is not used by something else
        query = model_query(models.Product).filter_by(name=name)
        query.delete()

    # TODO(chmou): Make those filters working (they don't do anything yet)
    def get_all_products(self, tenant_id, admin=False,
                         filters=None, limit=None,
                         marker=None, sort_key=None,
                         sort_dir=None):
        sort_key = sort_key or 'name'  # TODO(chmouel): sort by ID
        query = model_query(models.Product)

        # NOTE(chmou): This would list everthing when in admins
        if not admin:
            query = query.join(models.Subscriptions).filter(
                tenant_id == models.Subscriptions.tenant_id)
        return _paginate_query(models.Product, limit, marker,
                               sort_key, sort_dir, query)

    def get_product_by_name(self, name, tenant_id, admin=False):
        query = model_query(models.Product).filter_by(name=name)

        if not admin:
            query = query.join(models.Subscriptions).filter(
                tenant_id == models.Subscriptions.tenant_id)
        try:
            return query.one()
        except saladier.db.sqlalchemy.exc.NoResultFound:
            raise exception.ProductNotFound(name=name)

    # TODO(chmou): we are doing product_name thing for product_version but we
    # really should switch to id soon!
    def create_product_version(self, product_name, version, uri):
        query = model_query(models.ProductVersion)
        if query.filter_by(product_name=product_name, version=version).all():
            raise exception.ProductVersionAlreadyExists(product_name)
        new = models.ProductVersion(version=version,
                                    product_name=product_name,
                                    uri=uri)
        new.save()

    def get_product_version_by_id(self, id, session=None):
        query = model_query(models.ProductVersion,
                            session=session).filter_by(id=id)
        try:
            return query.one()
        except saladier.db.sqlalchemy.exc.NoResultFound:
            raise exception.ProductVersionNotFound(id=id)

    def get_all_product_versions(self, product_name):
        query = model_query(models.ProductVersion)
        res = query.filter_by(product_name=product_name).all()
        # TODO(chmou): filtering/paging and such
        return res

    def delete_product_versions(self, product_name, version):
        query = model_query(models.ProductVersion).filter_by(
            product_name=product_name, version=version)
        query.delete()

    def create_platform(self, name, location, contact, tenant_id):
        platform = models.Platform(name=name, location=location,
                                   contact=contact, tenant_id=tenant_id)

        try:
            platform.save()
        except db_exc.DBDuplicateEntry:
            raise exception.PlatformAlreadyExists(name)

    def delete_platform_by_name(self, name):
        query = model_query(models.Platform).filter_by(name=name)
        query.delete()

    def get_all_platforms(self, filters=None, limit=None, marker=None,
                          sort_key=None, sort_dir=None):
        sort_key = sort_key or 'name'
        return _paginate_query(models.Platform, limit, marker,
                               sort_key, sort_dir)

    def get_platform_by_name(self, name):
        query = model_query(models.Platform).filter_by(name=name)
        try:
            return query.one()
        except saladier.db.sqlalchemy.exc.NoResultFound:
            raise exception.PlatformNotFound(name=name)

    # -*- Subscriptions -*-
    def create_subscription(self, tenant_id, product_name):
        query = models.Subscriptions(tenant_id=tenant_id,
                                     product_name=product_name)
        try:
            query.save()
        except db_exc.DBDuplicateEntry:
            raise exception.SubscriptionAlreadyExists(product_name)

    def delete_subscription(self, product_name, tenant_id):
        model = (model_query(models.Subscriptions).
                 filter_by(product_name=product_name).
                 filter_by(tenant_id=tenant_id))
        model.delete()

    def get_subscriptions_for_tenant_id(self, tenant_id):
        query = model_query(models.Subscriptions).filter_by(
            tenant_id=tenant_id)
        return query.all()

    def add_version_status(self, platform_name, product_version_id, status,
                           logs_location):
        versions_status = (model_query(models.ProductVersionStatus).
                           filter_by(platform_name=platform_name).
                           filter_by(product_version_id=product_version_id).
                           first())

        if versions_status:
            raise exception.ProductVersionStatusAlreadyExists(
                "%s,%s" % (platform_name, product_version_id))

        session = get_session()
        with session.begin():
            platform = self.get_platform_by_name(platform_name)
            product_version = self.get_product_version_by_id(
                product_version_id, session=session)
            product_version_status = models.ProductVersionStatus(
                status=status, logs_location=logs_location)
            product_version_status.platform = platform
            product_version.platforms.append(product_version_status)
            try:
                product_version.save(session)
            except exception.SaladierFlushError:
                raise exception.ProductVersionStatusInvalid(
                    name="%s, %s" % (platform_name, product_version_id))

    def get_version_status(self, platform_name, product_version_id):
        query = model_query(models.ProductVersionStatus)
        try:
            return query.filter_by(platform_name=platform_name,
                                   product_version_id=product_version_id).one()
        except saladier.db.sqlalchemy.exc.NoResultFound:
            raise exception.ProductVersionStatusNotFound(
                id="%s,%s" % (platform_name, product_version_id))

    def get_all_version_status(self):
        return model_query(models.ProductVersionStatus).all()

    def update_version_status(self, platform_name, product_version_id,
                              new_status, new_logs_location):

        product_version_status = self.get_version_status(platform_name,
                                                         product_version_id)
        product_version_status.status = new_status
        product_version_status.logs_location = new_logs_location
        product_version_status.save()

    def delete_version_status(self, platform_name, product_version_id):
        query = model_query(models.ProductVersionStatus).filter_by(
            platform_name=platform_name, product_version_id=product_version_id)
        query.delete()
