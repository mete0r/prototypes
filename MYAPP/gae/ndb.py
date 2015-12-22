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

==> strong reference
--> weak reference

Session ====> Model state ====> Model
Session <---- Model state <---- Model



Entity states
-------------

0. Unknown

If an Entry is not in a Session, it's Unknown.

Unknown --getitem--> Absent
Unknown --getitem--> Persistent Clean
Unknown --setitem--> New Identified (an COMPLETE key will be assigned)
Unknown --add--> New Unidentified (an INCOMPLETE key will be assigned)

or else it's Known.

1. Absent

If an Entity is not stored in the DataStore nor in the Session, it's Absent.

Absent --setitem-> New Identified (an COMPLETE key will be assigned)

2. New

If a Model is not stored in the DataStore but is associated with a Session,
it's New.

If its key is ABSENT or INCOMPLETE, it's New Unidentified.
If its key is COMPLETE, it's New Identified.

New Unidentified --flush-> Persistent Clean (key will become COMPLETE)
New Unidentified --remove-> Absent
New Identified --delitem-> Absent
New Identified --flush-> Persistent Clean

3. Persistent

If a Model is stored in the DataStore, it's Persistent.  Its key is COMPLETE.

If its serialization is SAME with that in the DataStore, it's Persistent Clean.
If its serialization is DIFF with that in the DataStore, it's Persistent Dirty.
If Persistent Dirty model is not marked as deleted, it's Persistent Dirty Put.
If Persistent Dirty model is marked as deleted, it's Persistent Dirty Delete.

Persistent Clean --delitem-> Persistent Dirty Delete
Persistent Clean --modify-> Persistent Dirty Put
Persistent Dirty Put --delitem-> Persistent Dirty Delete
Persistent Dirty Put --modify-> Persistent Dirty Put
Persistent Dirty Put --flush-> Persistent Clean (will be included
ndb.put_multi)
Persistent Dirty Delete --getitem-> raise KeyError
Persistent Dirty Delete --delitem-> raise KeyError
Persistent Dirty Delete --flush-> Absent (will be included ndb.delete_multi)

* Identified/Unidentified

If a Model has INCOMPLETE key, it's Unidentified.
If a Model has COMPLETE key, it's Identified.

If a Model is Persistent, it's Identified always.

* Clean/Dirty

If a Model has SAME serialization with the stored in the DataStore, it's Clean.
If a Model has DIFF serialization with the stored in the DataStore, it's Dirty.

* Pending Put/Delete

If a Model is New or Persistent Dirty Put, it's Pendin Put.
If a Model is Persistent Dirty Delete, it's Pending Delete.


Session
-------

Session does not assign keys, nor care of key contents. (complete,
string/integer id, etc)

'''
from __future__ import absolute_import
from __future__ import unicode_literals
from itertools import ifilter
import logging

from google.appengine.ext import ndb
from google.appengine.ext.ndb.polymodel import PolyModel


logger = logging.getLogger(__name__)


def serialize(ndb_model):
    if ndb_model is None:
        return None
    else:
        return ndb_model.__getstate__()


class Entry(object):

    def __init__(self, ndb_model, stored_serialization):
        self.ndb_model = ndb_model
        self.stored_serialization = stored_serialization
        self.mark_to_delete = False

    @property
    def stored(self):
        return self.stored_serialization is not None

    @property
    def present(self):
        return self.ndb_model is not None

    @property
    def absent(self):
        return not self.stored and self.ndb_model is None

    @property
    def new(self):
        return not self.stored and self.ndb_model is not None

    @property
    def new_identified(self):
        return (self.new and
                self.ndb_model.key is not None and
                self.ndb_model.key.id() is not None)

    @property
    def new_unidentified(self):
        return self.new and (self.ndb_model.key is None or
                             self.ndb_model.key.id() is None)

    @property
    def persistent(self):
        return self.stored

    @property
    def persistent_clean(self):
        return (self.stored and self.present and
                serialize(self.ndb_model) == self.stored_serialization)

    @property
    def persistent_dirty(self):
        return (self.persistent_dirty_put or
                self.persistent_dirty_delete)

    @property
    def persistent_dirty_put(self):
        return (self.stored and self.present and
                serialize(self.ndb_model) != self.stored_serialization)

    @property
    def persistent_dirty_delete(self):
        return (self.stored and not self.present)

    @property
    def state(self):
        if self.absent:
            return 'absent'
        if self.new_identified:
            return 'new-identified'
        if self.new_unidentified:
            return 'new-unidentified'
        if self.persistent_clean:
            return 'persistent-clean'
        if self.persistent_dirty_put:
            return 'persistent-dirty-put'
        if self.persistent_dirty_delete:
            return 'persistent-dirty-delete'
        assert False

    def onPut(self):
        self.stored_serialization = serialize(self.ndb_model)

    def onDelete(self):
        self.stored_serialization = None
        self.ndb_model = None


class Session(object):

    def __init__(self):
        self.identified = {}
        self.unidentified = []

    def __getitem__(self, key):
        assert key.id() is not None

        if key in self.identified:
            entry = self.identified[key]
            if entry.ndb_model is None:
                assert not entry.present
                raise KeyError(key)
            assert entry.present
            assert entry.ndb_model.key == key
            return entry.ndb_model

        ndb_model = key.get()
        entry = Entry(ndb_model, serialize(ndb_model))
        self.identified[key] = entry

        if ndb_model is None:
            assert entry.state == 'absent', entry.state
            raise KeyError(key)
        else:
            ndb_model.__session__ = self
            assert entry.state == 'persistent-clean', entry.state
            return ndb_model

    def __setitem__(self, key, ndb_model):
        assert key.id() is not None

        entry = Entry(ndb_model, None)
        self.identified[key] = entry
        ndb_model.key = key
        ndb_model.__session__ = self
        assert entry.state == 'new-identified', entry.state

    def __delitem__(self, key):
        assert key.id() is not None

        entry = self.identified.get(key)
        if entry is None:
            # unknown
            entry = Entry(None, True)
            self.identified[key] = entry
            assert entry.persistent
            assert entry.state == 'persistent-dirty-delete', entry.state
            return

        if entry.ndb_model is None:
            raise KeyError(key)

        assert entry.new or entry.persistent, entry.state
        if entry.new:
            entry.ndb_model.__session__ = None
            entry.ndb_model = None
            del self.identified[key]
        elif entry.persistent:
            entry.ndb_model.__session__ = None
            entry.ndb_model = None
            assert entry.state == 'persistent-dirty-delete', entry.state

    def __contains__(self, key):
        try:
            self[key]
        except KeyError:
            return False
        else:
            return True

    def add(self, ndb_model):
        assert ndb_model is not None

        ndb_model.key = ndb.Key(type(ndb_model), None)
        ndb_model.__session__ = self
        entry = Entry(ndb_model, None)
        self.unidentified.append(entry)
        assert entry.state == 'new-unidentified', entry.state
        return entry

    def remove(self, ndb_model):
        assert ndb_model is not None

        entry = None
        for entry in self.unidentified:
            if entry.ndb_model is ndb_model:
                # Found
                break

        if entry is None:
            # Not found
            return

        # it will raise ValueError if not exists
        self.unidentified.remove(entry)

        assert entry.state == 'new-unidentified', entry.state
        ndb_model.__session__ = None
        entry.ndb_model = None
        assert entry.state == 'absent', entry.state
        return entry

    def query(self, q):
        self.flush()
        for ndb_model in q:
            key = ndb_model.key
            entry = Entry(ndb_model, serialize(ndb_model))
            self.identified[key] = entry

            if ndb_model is None:
                assert entry.state == 'absent', entry.state
            else:
                ndb_model.__session__ = self
                assert entry.state == 'persistent-clean', entry.state
            yield ndb_model

    def delete_query(self, q):
        self.flush()
        for key in q:
            try:
                del self[key]
            except KeyError:
                pass

    def flush(self):
        to_put = filter(lambda e: e.new or e.persistent_dirty_put,
                        self.identified.values() + self.unidentified)
        to_put_keys = ndb.put_multi(e.ndb_model for e in to_put)
        map(Entry.onPut, to_put)
        assert all(e.state == 'persistent-clean' for e in to_put)

        # move new-unidentified to identified
        for e in self.unidentified:
            key = e.ndb_model.key
            assert key not in self.identified
            self.identified[key] = e
        self.unidentified = []

        to_delete = list((k, e) for k, e in self.identified.items()
                         if e.persistent_dirty_delete)
        to_delete_keys = list(k for k, e in to_delete)
        ndb.delete_multi(to_delete_keys)
        map(Entry.onDelete, (e for k, e in to_delete))

        return set(to_put_keys + to_delete_keys)


class Node(PolyModel):
    '''


    1. Root node construction

    ndb.Key is assigned through this tree system, except the root node.

    root node should be created by following procedure:

    1) root key is known and the model is stored: root = session[key]
    2) the model is not stored - A) determine key B) associate with a Session

        root = Node()
        root_key = ndb.Key(Node, 'ROOT')
        session[root_key] = root

    or

        root = Node()
        session.add(root)

    then

        session.flush()

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
