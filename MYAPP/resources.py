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

from zope.interface import implements

from .interfaces import IDocument
from .interfaces import IFolder


def root_factory(request):
    root = Folder()
    root.__name__ = ''
    root['index'] = Document('Index', '<p>This is folder index.</p>')
    root['foo'] = Document('Foo', '<p>Foo content</p>')
    root['folder'] = folder = Folder()
    folder['bar'] = Document('Bar', '<p>Bar content</p>')
    return root


class Node(object):

    __parent__ = None
    __name__ = None


class Folder(Node):
    implements(IFolder)

    def __init__(self):
        self._children = {}

    def __getitem__(self, name):
        return self._children[name]

    def __setitem__(self, name, child):
        child.__parent__ = self
        child.__name__ = name
        self._children[name] = child

    def __delitem__(self, name):
        del self._children[name]

    @property
    def children(self):
        for name in self._children:
            yield self._children[name]


class Document(Node):
    implements(IDocument)

    title = None
    html_content = None

    def __init__(self, title, html_content):
        self.title = title
        self.html_content = html_content
