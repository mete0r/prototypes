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

from pyramid.view import view_config

from .bowerstatic import bootstrap_css
from .bowerstatic import bootstrap_js
from .interfaces import IDocument
from .interfaces import IFolder


@view_config(context=IDocument, request_method='GET',
             renderer='templates/document_view.pt')
def document_view(context, request):
    request.include(bootstrap_css)
    request.include(bootstrap_js)
    return {
    }


@view_config(context=IFolder, request_method='GET',
             renderer='templates/folder_view.pt')
def folder_view(context, request):
    request.include(bootstrap_css)
    request.include(bootstrap_js)
    return {
    }
