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

from pyramid_layout.panel import panel_config

from .interfaces import IFolder
from .interfaces import IDocument
from .interfaces import INavItem
from .interfaces import INavItemCollection
from .interfaces import INavItemSeparator


@panel_config(name='navbar',
              renderer='templates/navbar.pt')
def navbar(context, request, brand_name, title=''):
    return {
        'brand_name': brand_name,
        'title': title,
    }


@panel_config(name='nav',
              context=INavItemCollection,
              renderer='templates/nav.pt')
def nav(context, request):
    return {
    }


@panel_config(name='navitem',
              context=INavItem,
              renderer='templates/navitem.pt')
def navitem(context, request):
    return {
    }


@panel_config(name='navitem',
              context=INavItemCollection,
              renderer='templates/navitem_dropdown.pt')
def navitem_dropdown(context, request):
    return {
    }


@panel_config(name='navitem',
              context=INavItemSeparator,
              renderer='templates/navitem_separator.pt')
def navitem_separator(context, request):
    return {
    }


@panel_config(name='sidebar',
              context=IFolder,
              renderer='templates/sidebar_folder.pt')
def sidebar_folder(context, request, **kwargs):
    values = {
        'title': 'Subfolders',
        'children': filter(lambda item: IFolder.providedBy(item),
                           context.children),
    }
    values.update(kwargs)
    return values


@panel_config(name='sidebar',
              context=IDocument,
              renderer='templates/sidebar_document.pt')
def sidebar_document(context, request, **kwargs):
    values = {
        'title': 'Sidebar',
        'content': '',
    }
    values.update(kwargs)
    return values


@panel_config(name='folderitem',
              context=IFolder,
              renderer='templates/folderitem.pt')
def folderitem_folder(context, request):
    return {
        'title': context.__name__,
    }


@panel_config(name='folderitem',
              context=IDocument,
              renderer='templates/folderitem.pt')
def folderitem_document(context, request):
    return {
        'title': context.title,
    }


@panel_config(name='glyphicon',
              context=IFolder,
              renderer='templates/glyphicon.pt')
def glyphicon_folder(context, request):
    return {
        'glyphicon': 'glyphicon glyphicon-folder-close',
    }


@panel_config(name='glyphicon',
              context=IDocument,
              renderer='templates/glyphicon.pt')
def glyphicon_document(context, request):
    return {
        'glyphicon': 'glyphicon glyphicon-file',
    }
