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
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

from unittest import TestCase

from .layer_testbed import TestbedLayer


class SessionTest(TestCase):

    layer = TestbedLayer

    def make_one(self):
        from MYAPP.gae.ndb import Session
        return Session()

    def find_unidentified_entry(self, session, node):
        for entry in session.unidentified:
            if entry.ndb_model == node:
                return entry

    def test_unknown_getitem_absent(self):
        from google.appengine.ext.ndb import Key
        from MYAPP.gae.ndb import Node

        session = self.make_one()
        key = Key(Node, 'ROOT')

        try:
            session[key]
        except KeyError:
            pass
        else:
            assert False, 'KeyError expected'

        entry = session.identified[key]
        self.assertEquals('absent', entry.state)

    def test_unknown_getitem_persistent_clean(self):
        from google.appengine.ext.ndb import Key
        from MYAPP.gae.ndb import Node

        key = Key(Node, 'ROOT')
        node = Node()
        node.key = key
        node.put()
        session = self.make_one()

        found = session[key]

        entry = session.identified[key]
        self.assertEquals(node.key, found.key)
        self.assertEquals('persistent-clean', entry.state)

    def test_unknown_setitem_new_identified(self):
        from google.appengine.ext.ndb import Key
        from MYAPP.gae.ndb import Node

        session = self.make_one()
        node = Node()
        key = Key(Node, 'ROOT')

        session[key] = node

        entry = session.identified[key]
        self.assertEquals('new-identified', entry.state)

    def test_unknown_add_new_unidentified(self):
        from MYAPP.gae.ndb import Node

        session = self.make_one()
        node = Node()

        entry = session.add(node)

        self.assertEquals('new-unidentified', entry.state)

    def test_absent_setitem_new_identified(self):
        from google.appengine.ext.ndb import Key
        from MYAPP.gae.ndb import Node
        from MYAPP.gae.ndb import Entry

        key = Key(Node, 'ROOT')
        session = self.make_one()
        session.identified[key] = Entry(None, None)
        assert session.identified[key].state == 'absent'
        node = Node()

        session[key] = node

        entry = session.identified[key]
        self.assertEquals('new-identified', entry.state)

    def test_new_unidentified_flush_persistent_clean(self):
        from MYAPP.gae.ndb import Node

        session = self.make_one()
        node = Node()
        entry = session.add(node)
        assert entry.state == 'new-unidentified'

        flushed = session.flush()

        self.assertEquals(set([node.key]), flushed)
        self.assertTrue(node.key in session.identified)
        self.assertEquals([], session.unidentified)
        self.assertEquals('persistent-clean', entry.state)

    def test_new_unidentified_remove_unknown(self):
        from MYAPP.gae.ndb import Node

        session = self.make_one()
        node = Node()
        entry = session.add(node)
        assert entry.state == 'new-unidentified'

        session.remove(node)

        self.assertEquals({}, session.identified)
        self.assertEquals([], session.unidentified)

    def test_new_identitifed_flush_persistent_clean(self):
        from google.appengine.ext.ndb import Key
        from MYAPP.gae.ndb import Node

        session = self.make_one()

        node = Node()
        node_key = Key(Node, 'ROOT')
        session[node_key] = node
        entry = session.identified[node_key]
        assert entry.state == 'new-identified'

        flushed = session.flush()
        self.assertEquals(set([node_key]), flushed)
        self.assertEquals('persistent-clean', entry.state)

    def test_new_identified_delitem_unknown(self):
        from google.appengine.ext.ndb import Key
        from MYAPP.gae.ndb import Node

        session = self.make_one()

        node = Node()
        node_key = Key(Node, 'ROOT')
        session[node_key] = node
        entry = session.identified[node_key]
        assert entry.state == 'new-identified'

        del session[node_key]

        self.assertEquals({}, session.identified)
        self.assertEquals([], session.unidentified)

    def test_persistent_clean_delitem_persistent_dirty_delete(self):
        from google.appengine.ext.ndb import Key
        from MYAPP.gae.ndb import Node

        session = self.make_one()
        node = Node()
        node_key = Key(Node, 'ROOT')
        session[node_key] = node
        session.flush()
        assert session.identified[node_key].state == 'persistent-clean'
        entry = session.identified[node_key]

        del session[node.key]

        self.assertEquals('persistent-dirty-delete', entry.state)

    def test_persistent_clean_modify_persistent_dirty_put(self):
        from google.appengine.ext.ndb import Key
        from google.appengine.ext.ndb import StringProperty
        from MYAPP.gae.ndb import Node

        class Content(Node):
            title = StringProperty()

        session = self.make_one()
        node = Content(title='hello')
        node_key = Key(Content, 'ROOT')
        session[node_key] = node
        session.flush()
        assert session.identified[node_key].state == 'persistent-clean'

        node.title = 'world'

        entry = session.identified[node_key]
        self.assertEquals('persistent-dirty-put', entry.state)

    def test_persistent_dirty_put_delitem_persistent_dirty_delete(self):
        from google.appengine.ext.ndb import Key
        from google.appengine.ext.ndb import StringProperty
        from MYAPP.gae.ndb import Node

        class Content(Node):
            title = StringProperty()

        session = self.make_one()
        node = Content()
        node_key = Key(Content, 'ROOT')
        session[node_key] = node
        session.flush()
        assert session.identified[node_key].state == 'persistent-clean'
        node.title = 'hello'
        entry = session.identified[node_key]
        assert entry.state == 'persistent-dirty-put'

        del session[node_key]

        self.assertEquals('persistent-dirty-delete', entry.state)

    def test_persistent_dirty_put_modify_persistent_dirty_put(self):
        from google.appengine.ext.ndb import Key
        from google.appengine.ext.ndb import StringProperty
        from MYAPP.gae.ndb import Node

        class Content(Node):
            title = StringProperty()

        session = self.make_one()
        node = Content(title='hello')
        node_key = Key(Content, 'ROOT')
        session[node_key] = node
        session.flush()
        assert session.identified[node_key].state == 'persistent-clean'
        node.title = 'world'
        entry = session.identified[node_key]
        assert entry.state == 'persistent-dirty-put'

        node.title = 'foobar'

        self.assertEquals('persistent-dirty-put', entry.state)

    def test_persistent_dirty_put_flush_persistent_clean(self):
        from google.appengine.ext.ndb import Key
        from google.appengine.ext.ndb import StringProperty
        from MYAPP.gae.ndb import Node

        class Content(Node):
            title = StringProperty()

        session = self.make_one()
        node = Content(title='hello')
        node_key = Key(Content, 'ROOT')
        session[node_key] = node
        session.flush()
        assert session.identified[node_key].state == 'persistent-clean'
        node.title = 'world'
        entry = session.identified[node_key]
        assert entry.state == 'persistent-dirty-put'

        session.flush()

        self.assertEquals('persistent-clean', entry.state)

    def test_persistent_dirty_delete_getitem_raise_keyerror(self):
        from google.appengine.ext.ndb import Key
        from MYAPP.gae.ndb import Node

        session = self.make_one()
        node = Node()
        node_key = Key(Node, 'ROOT')
        session[node_key] = node
        session.flush()
        assert session.identified[node_key].state == 'persistent-clean'
        entry = session.identified[node_key]
        del session[node.key]
        assert entry.state == 'persistent-dirty-delete'

        try:
            session[node.key]
        except KeyError:
            pass
        else:
            assert False, 'KeyError expected'

    def test_persistent_dirty_delete_delitem_raise_keyerror(self):
        from google.appengine.ext.ndb import Key
        from MYAPP.gae.ndb import Node

        session = self.make_one()
        node = Node()
        node_key = Key(Node, 'ROOT')
        session[node_key] = node
        session.flush()
        assert session.identified[node_key].state == 'persistent-clean'
        entry = session.identified[node_key]
        del session[node.key]
        assert entry.state == 'persistent-dirty-delete'

        try:
            del session[node.key]
        except KeyError:
            pass
        else:
            assert False, 'KeyError expected'

    def test_persistent_dirty_delete_flush_absent(self):
        from google.appengine.ext.ndb import Key
        from MYAPP.gae.ndb import Node

        session = self.make_one()
        node = Node()
        node_key = Key(Node, 'ROOT')
        session[node_key] = node
        session.flush()
        assert session.identified[node_key].state == 'persistent-clean'
        entry = session.identified[node_key]
        del session[node.key]
        assert entry.state == 'persistent-dirty-delete'

        flushed = session.flush()

        self.assertTrue(node_key in flushed)
        self.assertTrue(node_key in session.identified)
        self.assertEquals('absent', entry.state)
