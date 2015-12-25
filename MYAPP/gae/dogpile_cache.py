# -*- coding: utf-8 -*-
#
#   MYAPP : SOME_DESCRIPTION
#   Copyright (C) 2015 mete0r <mete0r@sarangbang.or.kr>
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU Affero General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU Affero General Public License for more details.
#
#   You should have received a copy of the GNU Affero General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
'''
dogpile.cache backend backed by google.appengine.ext.ndb

TODO: cron to reap timeout sessions
'''
from __future__ import absolute_import
from __future__ import unicode_literals
import logging

from google.appengine.ext import ndb
from dogpile.cache.api import CacheBackend
from dogpile.cache.api import CachedValue
from dogpile.cache.api import NO_VALUE


logger = logging.getLogger(__name__)


class DogpileCacheRegion(ndb.Model):
    pass


class DogpileCacheEntry(ndb.Model):
    ct = ndb.ComputedProperty(lambda self: self.metadata['ct'])
    payload = ndb.BlobProperty()
    metadata = ndb.JsonProperty()

    @property
    def cached_value(self):
        cached_value = CachedValue(self.payload, self.metadata)
        return cached_value


def cached_value_from_entry(entry):
    if entry is None:
        return NO_VALUE
    return entry.cached_value


class NDBBackend(CacheBackend):

    def __init__(self, arguments):
        logger.debug('NDBBackend: %r', arguments)
        self.namespace = ndb.Key(DogpileCacheRegion, arguments['namespace'])

    def namespaced_key(self, key):
        return ndb.Key(DogpileCacheEntry, key, parent=self.namespace)

    def make_entry(self, key, cached_value):
        payload, metadata = cached_value
        entry = DogpileCacheEntry(payload=payload, metadata=metadata)
        entry.key = self.namespaced_key(key)
        return entry

    def get(self, key):
        ndbkey = self.namespaced_key(key)
        entry = ndbkey.get()
        return cached_value_from_entry(entry)

    def get_multi(self, keys):
        ndbkeys = [self.namespaced_key(key) for key in keys]
        entries = ndb.get_multi(ndbkeys)
        return [cached_value_from_entry(entry) for entry in entries]

    def set(self, key, cached_value):
        entry = self.make_entry(key, cached_value)
        entry.put()

    def set_multi(self, mapping):
        entries = [self.make_entry(key, cached_value)
                   for key, cached_value in mapping.items()]
        ndb.put_multi(entries)

    def delete(self, key):
        ndbkey = self.namespaced_key(key)
        ndbkey.delete()

    def delete_multi(self, keys):
        ndbkeys = [self.namespaced_key(key) for key in keys]
        ndb.delete_multi(ndbkeys)
