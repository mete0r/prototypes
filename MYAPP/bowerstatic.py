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

bower = bowerstatic.Bower()

components = bower.components(
    'components',
    bowerstatic.module_relative_path('bower_components')
)

local_components = bower.local_components('local', components)

theme = local_components.component(
    bowerstatic.module_relative_path('static/theme'),
    version=None
)

jquery_js = components.resource('jquery/dist/jquery.js')
bootstrap_css = local_components.resource('theme/css/bootstrap.css')
bootstrap_js = components.resource('bootstrap/dist/js/bootstrap.js',
                                   dependencies=[jquery_js])


def includeme(config):
    config.add_request_method(request_include, 'include')
    config.add_tween(__name__ + '.tween_factory')


def request_include(request, *args, **kwargs):
    include = local_components.includer(request.environ)
    return include(*args, **kwargs)


def tween_factory(handler, registry):
    injector = bowerstatic.InjectorTween(bower, handler)
    publisher = bowerstatic.PublisherTween(bower, injector)
    return publisher
