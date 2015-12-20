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

    def test_associate_free(self):
        from MYAPP.gae.ndb import Node

        session = self.make_one()

        node = Node()
        self.assertRaises(AssertionError,
                          session.associate,
                          node, stored=False)

    def test_associate_new(self):
        from google.appengine.ext import ndb
        from MYAPP.gae.ndb import Node

        session = self.make_one()

        node = Node()
        node.key = ndb.Key(Node, 'named')
        self.assertEquals('pending',
                          session.associate(node, stored=False))

    def test_associate_pending(self):
        from google.appengine.ext import ndb
        from MYAPP.gae.ndb import Node

        session = self.make_one()

        node = Node()
        node.key = ndb.Key(Node, 'named')
        assert 'pending' == session.associate(node, stored=False)
        self.assertRaises(AssertionError,
                          session.associate,
                          node, stored=False)

    def test_associate_persistent(self):
        from google.appengine.ext import ndb
        from MYAPP.gae.ndb import Node

        session = self.make_one()

        node = Node()
        node.key = ndb.Key(Node, 'named')
        node.put()
        assert 'persistent' == session.associate(node, stored=True)
        self.assertRaises(AssertionError,
                          session.associate,
                          node, stored=True)

    def test_associate_detached(self):
        from google.appengine.ext import ndb
        from MYAPP.gae.ndb import Node

        session = self.make_one()

        node = Node()
        node.key = ndb.Key(Node, 'named')
        node.put()
        self.assertEquals('persistent',
                          session.associate(node, stored=True))
