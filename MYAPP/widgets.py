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
from deform.widget import RichTextWidget
from pkg_resources import resource_filename


def includeme(config):
    deform_templates = resource_filename('deform', 'templates')
    my_templates = resource_filename('MYAPP', 'templates/deform')
    search_path = (my_templates, deform_templates)
    Form.set_zpt_renderer(search_path)


class RichTextInlineWidget(RichTextWidget):

    template = 'richtext-inline.pt'
    default_options = (RichTextWidget.default_options +
                       (('inline', True),
                        ('hidden_input', False)))
