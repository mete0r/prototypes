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

from ...interfaces import IAdd
from ...interfaces import IEdit
from ...interfaces import IFolder
from ..ndb import Node
from .node import NodeSchema


logger = logging.getLogger(__name__)


def includeme(config):
    register_components(config.registry)


def register_components(components):
    components.registerAdapter(FolderEdit, (Folder, IRequest), IEdit)
    components.registerAdapter(FolderAddFolder, (Folder, IRequest), IAdd,
                               'folder')


@implementer(IFolder)
class Folder(Node):

    __acl__ = [
        (Allow, Everyone, 'view'),
        (Allow, Everyone, 'add'),
        (Allow, Everyone, 'edit'),
        (Allow, Everyone, 'upload'),
        (Allow, Everyone, 'delete'),
    ]

    title = ndb.StringProperty()

    @property
    def children(self):
        return self.values()


class FolderSchema(NodeSchema):
    pass


@implementer(IAdd)
class FolderAddFolder(object):

    def __init__(self, context, request):
        self.context = context
        self.request = request

    @property
    def schema(self):
        return FolderSchema()

    @property
    def appstruct(self):
        return {
        }

    def __call__(self, appstruct):
        name = appstruct['title']
        node = Folder()
        self.context[name] = node
        logger.info('node %s added', node.__name__)
        return node


@implementer(IEdit)
class FolderEdit(object):

    def __init__(self, context, request):
        self.context = context
        self.request = request

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
        self.context.title = appstruct['title']
        logger.error('title: %s',
                     self.context.title)
