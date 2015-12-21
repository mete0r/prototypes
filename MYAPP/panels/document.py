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

from ..interfaces import IDocument


logger = logging.getLogger(__name__)


@panel_config(name='content',
              context=IDocument,
              renderer='../templates/resources/document/content.pt')
def document_content(context, request):
    return {
    }


@panel_config(name='sidebar',
              context=IDocument,
              renderer='../templates/resources/document/sidebar.pt')
def document_sidebar(context, request, **kwargs):
    values = {
        'title': 'Sidebar',
        'content': '',
    }
    values.update(kwargs)
    return values


@panel_config(name='folderitem',
              context=IDocument,
              renderer='../templates/folderitem.pt')
def document_folderitem(context, request):
    return {
        'title': context.title,
    }


@panel_config(name='glyphicon',
              context=IDocument,
              renderer='../templates/glyphicon.pt')
def document_glyphicon(context, request):
    return {
        'glyphicon': 'glyphicon glyphicon-file',
    }
