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

Model states:

1. Free

If a Model is not stored in the DataStore, has no key and is not associated
with a Session, it's Free.

Associate raises.

2. New

If a Model is not stored in the DataStore but has a key, then but is not
associated with a Session, it's New.

Associate to Pending.

3. Pending

If a Model is not stored in the DataStore but has a key and is associated with
a Session, it's Pending.

Associate raises.
Flush to Persistent.

4. Persistent

If a Model is stored in the DataStore, has a key and is associated with a
Session, it's Persistent.

Associate raises.

5. Dirty

If a Model is stored in the DataStore, has a key and is associated with a
Session but its contents are modified, it's Dirty.

Associate raises.
Flush to Persistent.

6. Detached

If a Model is stored in the DataStore, have a key but is not associated with a
Session, it's Detached.

Associate to Persistent.


Session does not assign keys, nor care of key contents. (complete,
string/integer id, etc)

'''
from __future__ import absolute_import
from __future__ import unicode_literals
from itertools import ifilter
from itertools import imap


from google.appengine.ext import ndb
from google.appengine.ext.ndb.polymodel import PolyModel


class Session(object):

    def __init__(self):
        self.entries = {}

    def __getitem__(self, key):
        if key in self.entries:
            entry = self.entries[key]
            return entry.ndb_model

        ndb_model = key.get()
        if ndb_model is None:
            raise KeyError(key)
        self.associate(ndb_model, stored=True)
        return ndb_model

    def __setitem__(self, key, ndb_model):
        entry = Entry(ndb_model, stored=False)
        assert entry.state == 'free', entry.state

        ndb_model.key = key
        assert entry.state == 'new', entry.state

        self.entries[key] = entry
        ndb_model.__session__ = self
        assert entry.state == 'pending'

    def __delitem__(self, key):
        if key not in self.entries:
            raise KeyError(key)
        self.detach(key)

    def __contains__(self, key):
        return key in self.entries

    def associate(self, ndb_model, stored):
        entry = Entry(ndb_model, stored=stored)
        assert not entry.associated or entry.ndb_model.__session__ is self,\
            entry.state
        if stored:
            assert entry.state in ('detached', 'persistent'), entry.state
        else:
            assert 'new' == entry.state, entry.state
        self.entries[ndb_model.key] = entry
        ndb_model.__session__ = self
        return entry.state

    def detach(self, key):
        entry = self.entries.pop(key, None)
        if entry is None:
            return key
        entry.ndb_model.__session__ = None
        assert entry.state == 'detached', entry.state
        return key

    def query(self, q):
        for ndb_model in q:
            self.associate(ndb_model, stored=True)
            yield ndb_model

    def delete_query(self, q):
        keys = imap(self.detach, q)
        ndb.delete_multi(keys)

    def flush(self):
        dirty_entries = ifilter(lambda e: e.state in ('pending', 'dirty'),
                                self.entries.values())
        dirty_models = imap(lambda e: e.ndb_model, dirty_entries)
        keys = ndb.put_multi(dirty_models)
        entries = imap(lambda k: self.entries[k], keys)
        map(Entry.onFlush, entries)
        return keys


class Entry(object):

    def __init__(self, ndb_model, stored):
        self._ndb_model = ndb_model
        self._serialized = ndb_model.__getstate__()
        self._stored = stored

    @property
    def ndb_model(self):
        return self._ndb_model

    @property
    def stored(self):
        return self._stored

    @property
    def haskey(self):
        key = self._ndb_model.key
        # it should have "complete" key, i.e. key id is not None
        return key is not None and key.id() is not None

    @property
    def associated(self):
        ''' Associated with a Session '''
        ndb_model = self.ndb_model
        session = ndb_model.__session__
        return session is not None and ndb_model.key in session

    @property
    def dirty(self):
        return self._serialized != self._ndb_model.__getstate__()

    @property
    def state(self):
        stored = self.stored
        haskey = self.haskey
        associated = self.associated

        statemap = {}
        statemap[False, False, False] = 'free'
        statemap[False, True, False] = 'new'
        statemap[False, True, True] = 'pending'
        statemap[True, True, True] = 'persistent'
        statemap[True, True, False] = 'detached'
        state = statemap[stored, haskey, associated]
        if state == 'persistent' and self.dirty:
            state = 'dirty'
        return state

    def onFlush(self):
        self._serialized = self._ndb_model.__getstate__()
        self._stored = True


class Node(PolyModel):
    '''


    1. Root node construction

    ndb.Key is assigned through this tree system, except the root node.

    root node should be created by following procedure:

    1) root key is known and the model is stored: root = session[key]
    2) the model is not stored - A) determine key B) associate with a Session

    root = Node()
    root.key = ndb.Key(Node, 'ROOT')
    session.associate(root, stored=True)

    2. Every nodes in the tree should have a key.

    ILocation-related operations are based on keys.

    3. Keys may not be persisted yet.

    Persistency is handled by Sessions.

    '''

    __parent__ = None
    __session__ = None

    @property
    def __name__(self):
        if self.__parent__ is None:
            return ''
        name = self.key.string_id()
        name = name.decode('utf-8')
        return name

    def __getitem__(self, name):
        key = make_child_key(self, name)
        item = self.__session__[key]
        if item is None:
            raise KeyError(name)
        item.__parent__ = self
        return item

    def __setitem__(self, name, item):
        key = make_child_key(self, name)
        if item.__session__ is not None and\
           item.__session__ is not self.__session__:
            raise ValueError()
        self.__session__[key] = item
        item.__parent__ = self

    def __delitem__(self, name):
        key = make_child_key(self, name)
        tree = query_descendants_keys(key)
        self.__session__.delete_query(tree)

    def __contains__(self, name):
        key = make_child_key(self, name)
        return key in self.__session__ or key.get() is not None

    def __iter__(self):
        return self.keys()

    def keys(self):
        for key in query_children_keys(self.key):
            yield key.string_id().decode('utf-8')

    def values(self):
        q = query_children(self.key)
        for child in self.__session__.query(q):
            child.__parent__ = self
            yield child

    def items(self):
        for child in self.values():
            if self.key == child.key.parent():
                name = child.key.string_id().decode('utf-8')
                yield name, child


def make_child_key(node, name):
    pair = (Node, name)
    pairs = node.key.pairs() + (pair,)
    key = ndb.Key(pairs=pairs)
    return key


def query_descendants_keys(key):
    q = Node.query(ancestor=key)
    keys = q.iter(keys_only=True)
    return keys


def query_children_keys(key):
    keys = query_descendants_keys(key)
    keys = ifilter(lambda k: k.parent() == key, keys)
    return keys


def query_children(key):
    q = Node.query(ancestor=key)
    models = q.iter()
    models = ifilter(lambda m: m.key.parent() == key, models)
    return models
