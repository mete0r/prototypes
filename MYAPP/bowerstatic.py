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

from zope.interface import Interface

from .framework.bowerstatic import IBower
from .framework.bowerstatic import IBowerComponents
from .framework.bowerstatic import IBowerLocalComponents


class IBootstrapJS(Interface):
    pass


class IBootstrapCSS(Interface):
    pass


def module_relative_path(path):
    import os.path
    path = os.path.join(os.path.dirname(__file__), path)
    path = os.path.realpath(path)
    return path


def includeme(config):
    bower = config.registry.getUtility(IBower)

    components = bower.components(
        'components',
        module_relative_path('bower_components')
    )

    local_components = bower.local_components('local', components)

    theme = local_components.component(
        module_relative_path('static/theme'),
        version=None
    )
    theme

    jquery_js = components.resource('jquery/dist/jquery.js')
    bootstrap_js = components.resource('bootstrap/dist/js/bootstrap.js',
                                       dependencies=[jquery_js])
    bootstrap_css = local_components.resource('theme/css/bootstrap.css')

    config.registry.registerUtility(components, IBowerComponents)
    config.registry.registerUtility(local_components, IBowerLocalComponents,
                                    'local')
    config.registry.registerUtility(bootstrap_js, IBootstrapJS)
    config.registry.registerUtility(bootstrap_css, IBootstrapCSS)
    config.add_request_method(request_include, 'include')


def request_include(request, *args, **kwargs):
    local_components = request.registry.getUtility(IBowerLocalComponents,
                                                   'local')
    include = local_components.includer(request.environ)
    return include(*args, **kwargs)
