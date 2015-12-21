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

from ..interfaces import IFolder


logger = logging.getLogger(__name__)


@panel_config(name='content',
              context=IFolder,
              renderer='../templates/resources/folder/content.pt')
def folder_content(context, request):
    return {
    }


@panel_config(name='sidebar',
              context=IFolder,
              renderer='../templates/resources/folder/sidebar.pt')
def folder_sidebar(context, request, **kwargs):
    values = {
        'title': 'Subfolders',
        'children': filter(lambda item: IFolder.providedBy(item),
                           context.children),
    }
    values.update(kwargs)
    return values


@panel_config(name='folderitem',
              context=IFolder,
              renderer='../templates/folderitem.pt')
def folder_folderitem(context, request):
    return {
        'title': context.__name__,
    }


@panel_config(name='glyphicon',
              context=IFolder,
              renderer='../templates/glyphicon.pt')
def folder_glyphicon(context, request):
    return {
        'glyphicon': 'glyphicon glyphicon-folder-close',
    }
