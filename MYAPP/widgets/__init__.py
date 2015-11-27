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

from deform.widget import FileUploadWidget
from deform.widget import RichTextWidget
from pkg_resources import resource_filename
import colander

from ..framework.deform import IDeformSearchPath

logger = logging.getLogger(__name__)


def includeme(config):
    my_templates = resource_filename('MYAPP', 'templates/deform')
    deform_search_path = config.registry.getUtility(IDeformSearchPath)
    deform_search_path.prepend(my_templates)


class RichTextInlineWidget(RichTextWidget):

    template = 'richtext-inline.pt'
    default_options = (RichTextWidget.default_options +
                       (('inline', True),
                        ('hidden_input', False)))


@colander.deferred
def deferred_html_widget(node, kw):
    return kw.get('html_widget', RichTextInlineWidget())


@colander.deferred
def deferred_fileupload_widget(node, kw):
    tmpstore = kw.get('tmpstore')
    if tmpstore is None:
        tmpstore = NullFileUploadTempStore()
    return FileUploadWidget(tmpstore)


class NullFileUploadTempStore(object):

    def __init__(self):
        self._d = {}

    def get(self, name, default=None):
        return self._d.get(name, default)

    def __getitem__(self, name):
        return self._d[name]

    def __setitem__(self, name, value):
        self._d[name] = value

    def __contains__(self, name):
        return name in self._d

    def preview_url(self, name):
        return None
