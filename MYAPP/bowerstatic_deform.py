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

import bowerstatic

from .bowerstatic import components
from .bowerstatic import local_components
from .bowerstatic import request_include
from .bowerstatic import jquery_js


def module_relative_path(path):
    import os.path
    path = os.path.join(os.path.dirname(__file__), path)
    path = os.path.realpath(path)
    return path


deform = local_components.component(
    module_relative_path('static/deform'),
    version=None
)

jquery_form_js =\
    components.resource('jquery-form/jquery.form.js',
                        dependencies=[jquery_js])
jquery_maskedinput_js =\
    components.resource('jquery.maskedinput/dist/jquery.maskedinput.js',
                        dependencies=[jquery_js])
jquery_sortable_js =\
    components.resource('jquery-sortable/source/js/jquery-sortable.js')
# deform_js =\
#     local_components.resource('deform/scripts/deform.js',
#                               dependencies=[jquery_form_js])


tinymce_js =\
    components.resource('tinymce/tinymce.js')


deform_requirements_registry = {
    'deform': [
        jquery_form_js,
        # 'deform:static/scripts/deform.js',
    ],
    'jquery.form': [
        jquery_form_js,
    ],
    'jquery.maskedinput': [
        jquery_maskedinput_js,
    ],
    'sortable': [
        jquery_sortable_js,
    ],
    'tinymce': [
        tinymce_js,
    ],
}


def includeme(config):
    config.add_request_method(request_include_deform_widget,
                              'include_deform_widget')


def request_include_deform_widget(request, deform_widget):
    request.layout_manager.layout.use_deform = True
    widget_requirements = deform_widget.get_widget_requirements()
    for requirement, version in widget_requirements:
        if version is not None:
            pass  # TODO: version check
        for resource in deform_requirements_registry[requirement]:
            request_include(request, resource)
