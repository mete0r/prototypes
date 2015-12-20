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

from google.appengine.ext import ndb
from pyramid.interfaces import IRequest
from pyramid.security import Allow
from pyramid.security import Authenticated
from pyramid.security import Everyone
from zope.interface import implementer
import colander

from ...interfaces import IAdd
from ...interfaces import IEdit
from ...interfaces import IDownloadable
from ...interfaces import IDocument
from ...widgets import deferred_html_widget
from ..ndb import Node
from .folder import Folder
from .node import NodeSchema


logger = logging.getLogger(__name__)


def includeme(config):
    register_components(config.registry)


def register_components(components):
    components.registerAdapter(DocumentEdit, (Document, IRequest), IEdit)
    components.registerAdapter(DocumentAddToFolder, (Folder, IRequest), IAdd,
                               'document')


@implementer(IDocument, IDownloadable)
class Document(Node):

    __acl__ = [
        (Allow, Everyone, 'view'),
        (Allow, Everyone, 'download'),
        (Allow, Everyone, 'edit'),
        (Allow, Everyone, 'delete'),
    ]

    title = ndb.StringProperty()
    html_content = ndb.TextProperty()

    content_type = 'text/html'

    @property
    def content_filename(self):
        return self.__name__

    @property
    def content_bytes(self):
        return self.html_content.encode('utf-8')


class DocumentSchema(NodeSchema):
    html_content = colander.SchemaNode(colander.String(),
                                       widget=deferred_html_widget)


@implementer(IAdd)
class DocumentAddToFolder(object):

    def __init__(self, context, request):
        self.context = context
        self.request = request

    @property
    def schema(self):
        return DocumentSchema()

    @property
    def appstruct(self):
        return {
        }

    def __call__(self, appstruct):
        node = Document(**appstruct)
        self.context[node.title] = node
        logger.info('node %s added', node.__name__)
        return node


@implementer(IEdit)
class DocumentEdit(object):

    def __init__(self, context, request):
        self.context = context
        self.request = request

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
