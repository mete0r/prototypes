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

from pyramid.config import Configurator
from pyramid.authentication import BasicAuthAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy

from .resources import root_factory
from .security import authenticate_userpass


def app_factory(global_config, **settings):
    authn_policy = BasicAuthAuthenticationPolicy(check=authenticate_userpass)
    authz_policy = ACLAuthorizationPolicy()

    config = Configurator(root_factory=root_factory, settings=settings)
    config.set_authentication_policy(authn_policy)
    config.set_authorization_policy(authz_policy)
    config.add_translation_dirs(*[
        'colander:locale',
        'deform:locale',
        'locale',
    ])
    config.include('pyramid_chameleon')
    config.include('pyramid_layout')
    config.include('.framework')
    config.include('.framework.bowerstatic')
    config.include('.bowerstatic')
    config.include('.framework.deform')
    config.include('.framework.deform.bowerstatic')
    config.include('.layouts')
    config.include('.panels')
    config.include('.renderers')
    config.include('.resources')
    config.include('.views')
    config.include('.widgets')
    config.add_static_view('static/deform', 'deform:static')

    return config.make_wsgi_app()
