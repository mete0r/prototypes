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
import logging

from zope.interface import implementer
from deform.widget import RichTextWidget
import colander

from .interfaces import IDocument
from .interfaces import IFolder
from .interfaces import IAdd
from .interfaces import IEdit


logger = logging.getLogger(__name__)


def includeme(config):
    register_components(config.registry)


def register_components(components):
    components.registerAdapter(FolderEdit, (Folder, ), IEdit)
    components.registerAdapter(FolderAddFolder, (Folder, ), IAdd, 'folder')
    components.registerAdapter(FolderAddDocument, (Folder, ), IAdd, 'document')
    components.registerAdapter(DocumentEdit, (Document, ), IEdit)


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


class NodeSchema(colander.MappingSchema):
    title = colander.SchemaNode(colander.String())


@implementer(IFolder)
class Folder(Node):

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


class FolderSchema(NodeSchema):
    pass


@implementer(IAdd)
class FolderAddFolder(object):

    def __init__(self, context):
        self.context = context

    @property
    def schema(self):
        return FolderSchema()

    def __call__(self, appstruct):
        name = appstruct['title']
        node = Folder()
        self.context[name] = node
        logger.info('node %s added', node.__name__)
        return node


@implementer(IAdd)
class FolderAddDocument(object):

    def __init__(self, context):
        self.context = context

    @property
    def schema(self):
        return DocumentSchema()

    def __call__(self, appstruct):
        node = Document(**appstruct)
        self.context[node.title] = node
        logger.info('node %s added', node.__name__)
        return node


@implementer(IEdit)
class FolderEdit(object):

    def __init__(self, context):
        self.context = context

    @property
    def schema(self):
        return FolderSchema()

    @property
    def appstruct(self):
        return {
            'title': self.context.__name__,
        }

    @appstruct.setter
    def appstruct_set(self, appstruct):
        self.context.__name__ = appstruct['title']
        logger.error('title: %s',
                     self.context.title)


@implementer(IDocument)
class Document(Node):

    title = None
    html_content = None

    def __init__(self, title, html_content):
        self.title = title
        self.html_content = html_content


class DocumentSchema(NodeSchema):
    html_content = colander.SchemaNode(colander.String(),
                                       widget=RichTextWidget())


@implementer(IEdit)
class DocumentEdit(object):

    def __init__(self, context):
        self.context = context

    @property
    def schema(self):
        return DocumentSchema()

    def getAppStruct(self):
        return {
            'title': self.context.title,
            'html_content': self.context.html_content,
        }

    def setAppStruct(self, appstruct):
        self.context.title = appstruct['title']
        self.context.html_content = appstruct['html_content']
        logger.error('title: %s, html_content: %s',
                     self.context.title,
                     self.context.html_content)

    appstruct = property(getAppStruct,
                         setAppStruct)
