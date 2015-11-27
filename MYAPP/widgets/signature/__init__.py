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
import os.path

from deform.compat import string_types
from deform.widget import Widget
import colander

from ...framework.bowerstatic import IBowerComponents
from ...framework.deform import IDeformSearchPath
from ...framework.deform.bowerstatic import IWidgetRequirementsRegistry


logger = logging.getLogger(__name__)


def includeme(config):
    my_templates = os.path.join(os.path.dirname(__file__), 'templates')
    deform_search_path = config.registry.getUtility(IDeformSearchPath)
    deform_search_path.prepend(my_templates)

    components = config.registry.getUtility(IBowerComponents)
    signature_pad_js =\
        components.resource('signature_pad/signature_pad.js')

    deform_widgets = config.registry.getUtility(IWidgetRequirementsRegistry)
    deform_widgets['signature_pad', None] = signature_pad_js


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
