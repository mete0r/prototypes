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

from deform import Form
from deform.compat import string_types
from deform.widget import FileUploadWidget
from deform.widget import RichTextWidget
from deform.widget import Widget
from pkg_resources import resource_filename
import colander


def includeme(config):
    deform_templates = resource_filename('deform', 'templates')
    my_templates = resource_filename('MYAPP', 'templates/deform')
    search_path = (my_templates, deform_templates)
    Form.set_zpt_renderer(search_path, debug=False)


class RichTextInlineWidget(RichTextWidget):

    template = 'richtext-inline.pt'
    default_options = (RichTextWidget.default_options +
                       (('inline', True),
                        ('hidden_input', False)))


class SignatureWidget(Widget):

    template = 'signature'
    readonly_template = 'readonly/signature'
    requirements = (('signature_pad', None),)

    def serialize(self, field, cstruct, **kw):
        if cstruct in (colander.null, None):
            cstruct = ''
        readonly = kw.get('readonly', self.readonly)
        template = readonly and self.readonly_template or self.template
        values = self.get_template_values(field, cstruct, kw)
        return field.renderer(template, **values)

    def deserialize(self, field, pstruct):
        if pstruct is colander.null:
            return colander.null
        elif not isinstance(pstruct, string_types):
            raise colander.Invalid(field.schema, 'Pstruct is not a string')
        if not pstruct:
            return colander.null
        return pstruct


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
