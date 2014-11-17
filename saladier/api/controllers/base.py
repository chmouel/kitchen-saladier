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
from pecan import rest


class BaseRestController(rest.RestController):
    def __init__(self):
        super(BaseRestController, self).__init__()


class APIBase(object):
    def __init__(self, sqlobj):
        for field in self.fields:  # NOTE(chmou): This should come from DB
            setattr(self, field, sqlobj.get(field))

    def as_dict(self):
        """Render this object as a dict of its fields."""
        return dict((k, getattr(self, k))
                    for k in self.fields
                    if hasattr(self, k))


class APIBaseCollections(object):
    def __init__(self, collections):
        self.collections = collections

    def as_dict(self):
        ret = []
        for c in self.collections:
            ret.append(self._type(c).as_dict())
        return {self.dict_field: ret}
