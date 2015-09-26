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
from six.moves import map as imap

from .interfaces import IFolder
from .interfaces import IDocument
from .interfaces import INavItem
from .interfaces import INavItemCollection
from .interfaces import INavItemSeparator
from .interfaces import IAddable
from .interfaces import IAdd
from .interfaces import IEditable
from .interfaces import IDeletable
from .interfaces import IDownloadable
from .interfaces import IUploadable


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


@panel_config(name='action-add-dropdown',
              context=IAddable,
              renderer='templates/action-add-dropdown.pt')
def action_add_dropdown(context, request):
    itemtypes = request.registry.getAdapters((context,), IAdd)
    itemtypes = imap(lambda x: x[0], itemtypes)
    return {
        'title': 'Add',
        'item_types': itemtypes,
    }


@panel_config(name='action-add',
              context=IAddable,
              renderer='templates/action-add.pt')
def action_add(context, request, type):
    return {
        'title': 'Add ' + type,
        'type': type,
    }


@panel_config(name='action-edit',
              context=IEditable,
              renderer='templates/action-edit.pt')
def action_edit(context, request):
    return {
        'title': 'Edit',
    }


@panel_config(name='action-delete',
              context=IDeletable,
              renderer='templates/action-delete.pt')
def action_delete(context, request):
    return {
        'title': 'Delete',
    }


@panel_config(name='action-download',
              context=IDownloadable,
              renderer='templates/action-download.pt')
def action_download(context, request):
    return {
        'title': 'Download',
    }


@panel_config(name='action-upload',
              context=IUploadable,
              renderer='templates/action-upload.pt')
def action_upload(context, request):
    return {
        'title': 'Upload',
    }


@panel_config(name='content',
              context=IFolder,
              renderer='templates/content_folder.pt')
def content_folder(context, request):
    return {
    }


@panel_config(name='content',
              context=IDocument,
              renderer='templates/content_document.pt')
def content_document(context, request):
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
