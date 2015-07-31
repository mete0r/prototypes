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

from unittest import TestCase


class GetPathSegTest(TestCase):

    def test_root(self):
        from ..location import get_pathseg
        root = DummyObject()
        root.__parent__ = None
        root.__name__ = ''
        self.assertEquals(get_pathseg(root), [])

    def test_one(self):
        from ..location import get_pathseg
        root = DummyObject()
        root.__parent__ = None
        root.__name__ = ''
        one = DummyObject()
        one.__parent__ = root
        one.__name__ = 'one'
        self.assertEquals(get_pathseg(one), ['one'])

    def test_two(self):
        from ..location import get_pathseg
        root = DummyObject()
        root.__parent__ = None
        root.__name__ = ''
        one = DummyObject()
        one.__parent__ = root
        one.__name__ = 'one'
        two = DummyObject()
        two.__parent__ = one
        two.__name__ = 'two'
        self.assertEquals(get_pathseg(two), ['one', 'two'])


class GetPathTest(TestCase):

    def test_root(self):
        from ..location import get_path
        root = DummyObject()
        root.__parent__ = None
        root.__name__ = ''
        self.assertEquals(get_path(root), '/')

    def test_one(self):
        from ..location import get_path
        root = DummyObject()
        root.__parent__ = None
        root.__name__ = ''
        one = DummyObject()
        one.__parent__ = root
        one.__name__ = 'one'
        self.assertEquals(get_path(one), '/one')

    def test_two(self):
        from ..location import get_path
        root = DummyObject()
        root.__parent__ = None
        root.__name__ = ''
        one = DummyObject()
        one.__parent__ = root
        one.__name__ = 'one'
        two = DummyObject()
        two.__parent__ = one
        two.__name__ = 'two'
        self.assertEquals(get_path(two), '/one/two')


class DummyObject(object):
    pass
