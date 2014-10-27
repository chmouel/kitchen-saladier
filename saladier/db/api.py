# -*- coding: utf-8 -*-
# Copyright (C) 2013 eNovance SAS <licensing@enovance.com>
#
# Author: Chmouel Boudjnah <chmouel@enovance.com>
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

        # TODO(chmouel): handle conflicts
        try:
            product.save()
        except db_exc.DBDuplicateEntry:
            raise exception.ProductAlreadyExists(name)

    def get_all_products(self, filters=None, limit=None,
                         marker=None, sort_key=None, sort_dir=None):
        sort_key = sort_key or 'name'  # TODO(chmouel): sort by ID
        return _paginate_query(models.Product, limit, marker,
                               sort_key, sort_dir)

    def get_product_by_name(self, name):
        query = model_query(models.Product).filter_by(name=name)
        return query.one()  # TODO(chmou): Handle NotFounds
