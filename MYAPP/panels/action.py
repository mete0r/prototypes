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

from pyramid_layout.panel import panel_config
from six.moves import map as imap

from ..interfaces import IAddable
from ..interfaces import IAdd
from ..interfaces import IEditable
from ..interfaces import IDeletable
from ..interfaces import IDownloadable
from ..interfaces import IUploadable


logger = logging.getLogger(__name__)


@panel_config(name='action-add-dropdown',
              context=IAddable,
              renderer='../templates/panels/action/add-dropdown.pt')
def action_add_dropdown(context, request):
    itemtypes = request.registry.getAdapters((context,), IAdd)
    itemtypes = imap(lambda x: x[0], itemtypes)
    return {
        'title': 'Add',
        'item_types': itemtypes,
    }


@panel_config(name='action-add',
              context=IAddable,
              renderer='../templates/panels/action/add.pt')
def action_add(context, request, type):
    return {
        'title': 'Add ' + type,
        'type': type,
    }


@panel_config(name='action-edit',
              context=IEditable,
              renderer='../templates/panels/action/edit.pt')
def action_edit(context, request):
    return {
        'title': 'Edit',
    }


@panel_config(name='action-delete',
              context=IDeletable,
              renderer='../templates/panels/action/delete.pt')
def action_delete(context, request):
    return {
        'title': 'Delete',
    }


@panel_config(name='action-download',
              context=IDownloadable,
              renderer='../templates/panels/action/download.pt')
def action_download(context, request):
    return {
        'title': 'Download',
    }


@panel_config(name='action-upload',
              context=IUploadable,
              renderer='../templates/panels/action/upload.pt')
def action_upload(context, request):
    return {
        'title': 'Upload',
    }
