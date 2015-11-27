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

from pkg_resources import resource_filename
from zope.interface import Interface
from zope.interface import implementer

from ..bowerstatic import IBower
from ..bowerstatic import IBowerComponents


logger = logging.getLogger(__name__)


def includeme(config):
    bower = config.registry.getUtility(IBower)
    components = config.registry.getUtility(IBowerComponents)

    jquery_js = components.resource('jquery/dist/jquery.js')
    jquery_form_js =\
        components.resource('jquery-form/jquery.form.js',
                            dependencies=[jquery_js])
    jquery_maskedinput_js =\
        components.resource('jquery.maskedinput/dist/jquery.maskedinput.js',
                            dependencies=[jquery_js])
    jquery_maskMoney_js =\
        components.resource('jquery.maskMoney/dist/jquery.maskMoney.js')
    jquery_sortable_js =\
        components.resource('jquery-sortable/source/js/jquery-sortable.js')
    modernizr_js =\
        components.resource('modernizr/modernizr.js')
    pickadate_picker_js =\
        components.resource('pickadate/lib/picker.js')
    pickadate_picker_date_js =\
        components.resource('pickadate/lib/picker.date.js')
    pickadate_picker_time_js =\
        components.resource('pickadate/lib/picker.time.js')
    pickadate_legacy_js =\
        components.resource('pickadate/lib/legacy.js')
    tinymce_js =\
        components.resource('tinymce/tinymce.js')

    # register deform:static asset directory as a local bower component
    deform_static = resource_filename('deform', 'static')
    deform_static = os.path.join(os.path.dirname(__file__))
    deform_components = bower.local_components('deform', components)
    # deform =\
    deform_components.component(deform_static, version=None)

    def request_include_deform_widget(request, deform_widget):
        request.layout_manager.layout.use_deform = True
        include = deform_components.includer(request.environ)

        widget_requirements_registry = request.registry.getUtility(
            IWidgetRequirementsRegistry)

        widget_requirements = deform_widget.get_widget_requirements()
        for requirement in widget_requirements:
            try:
                resources = widget_requirements_registry[requirement]
            except KeyError as e:
                logger.exception(e)
            else:
                for resource in resources:
                    include(resource)

    config.add_request_method(request_include_deform_widget,
                              'include_deform_widget')

#    deform_js =\
#        deform_components.resource('deform/scripts/deform.js',
#                                   dependencies=[jquery_form_js])
    # WORKAROUND
    # TODO: deform:static/scripts/deform.js
    deform_js = jquery_form_js

    widget_requirements_registry = WidgetRequirementsRegistry()
    config.registry.registerUtility(widget_requirements_registry,
                                    IWidgetRequirementsRegistry)
    widget_requirements_registry['deform', None] = [
        deform_js,
    ]
    widget_requirements_registry['jquery.form', None] = [
        jquery_form_js,
    ]
    widget_requirements_registry['jquery.maskedinput', None] = [
        jquery_maskedinput_js,
    ]
    widget_requirements_registry['jquery.maskMoney', None] = [
        jquery_maskMoney_js,
    ]
    widget_requirements_registry['sortable', None] = [
        jquery_sortable_js,
    ]
    widget_requirements_registry['tinymce', None] = [
        tinymce_js,
    ]
    widget_requirements_registry['modernizr', None] = [
        modernizr_js,
    ]
    widget_requirements_registry['pickadate', None] = [
        pickadate_picker_js,
        pickadate_picker_date_js,
        pickadate_picker_time_js,
        pickadate_legacy_js,
    ]


class IWidgetRequirementsRegistry(Interface):

    def __getitem__(requirement):
        ''' resolve bowerstatic resources with given deform requirement
        '''

    def __setitem__(requirement, resources):
        ''' register bowerstatic resources with given deform requirement
        '''


@implementer(IWidgetRequirementsRegistry)
class WidgetRequirementsRegistry(object):

    def __init__(self):
        self._registry = {}

    def __getitem__(self, requirement):
        name, version = requirement
        versions = self._registry[name]
        if version is None:
            # return anything; TODO: latest version
            for resources in versions.values():
                return resources
            raise KeyError(requirement)
        return versions[version]

    def __setitem__(self, requirement, resources):
        name, version = requirement
        self._registry.setdefault(name, {})
        versions = self._registry[name]
        versions[version] = resources
