# -*- coding: utf-8 -*-
#
#   METE0R-PROJECT: SOME_DESCRIPTION
#   Copyright (C) 2015-2018 mete0r <mete0r@sarangbang.or.kr>
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
try:
    from ConfigParser import ConfigParser
except ImportError:
    from configparser import ConfigParser
import io
import json
import logging
import os.path
import sys

from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.config import Configurator
from pyramid.httpexceptions import HTTPClientError
from pyramid.httpexceptions import HTTPNoContent
from pyramid.httpexceptions import HTTPServerError
from pyramid.renderers import render_to_response
from pyramid.security import Allow
from pyramid.security import Authenticated
from pyramid.security import Everyone
from pyramid.static import ManifestCacheBuster
from pyramid.view import view_config
from zope.interface import implementer
from zope.location import ILocation
import six


logger = logging.getLogger(__name__)


def app_factory(global_config, **settings):
    etc_directory = settings.setdefault(
        'etc-directory',
        os.path.join(sys.prefix, 'etc', 'METE0R-PROJECT'),
    )
    run_directory = settings.setdefault(
        'run-directory',
        os.path.join(sys.prefix, 'var', 'run', 'METE0R-PROJECT'),
    )
    lib_directory = settings.setdefault(
        'lib-directory',
        os.path.join(sys.prefix, 'var', 'lib', 'METE0R-PROJECT'),
    )
    cache_directory = settings.setdefault(
        'cache-directory',
        os.path.join(sys.prefix, 'var', 'cache', 'METE0R-PROJECT'),
    )
    logger.info('etc-directory: %s', etc_directory)
    logger.info('run-directory: %s', run_directory)
    logger.info('lib-directory: %s', lib_directory)
    logger.info('cache-directory: %s', cache_directory)

    credentials_ini = settings.get(
        'credentials.ini',
        os.path.join(etc_directory, 'credentials.ini'),
    )
    if os.path.exists(credentials_ini):
        logger.info('loading %s', credentials_ini)
        configparser = ConfigParser()
        configparser.read(credentials_ini)
        settings.update(
            dict(configparser.items('credentials'))
        )

    config = Configurator(settings=settings)
    config.set_root_factory(root_factory)
    config.add_translation_dirs(*[
        'locale',
    ])

    config.include('pyramid_jwt')
    config.set_jwt_authentication_policy()
    config.set_authorization_policy(
        ACLAuthorizationPolicy()
    )

    config.include('pyramid_chameleon')

    cachebuster_reload = settings.get(
        'manifestcachebuster.reload', 'false'
    )
    cachebuster_reload = cachebuster_reload == 'true'
    cachebuster = ManifestCacheBuster(
        'static/manifest.json',
        reload=cachebuster_reload,
    )
    config.add_static_view(name='static', path='static')
    config.add_cache_buster(
        'static', cachebuster,
    )

    config.include('pyramid_layout')

    config.scan(ignore=[
        b'.tests'
    ])
    config.commit()

    return config.make_wsgi_app()


def root_factory(request):
    return Site()


@view_config(context=HTTPClientError,
             accept='text/html',
             layout='cover')
@view_config(context=HTTPServerError,
             accept='text/html',
             layout='cover')
def httpexception_view(context, request):
    render_to_response('templates/httpexception.pt', {
    }, request=request, response=context)
    return context


@implementer(ILocation)
class Site(object):
    __name__ = ''
    __parent__ = None
    __acl__ = (
        (Allow, Everyone, 'read'),
        (Allow, Authenticated, 'write'),
    )


@view_config(context=Site,
             request_method='GET',
             accept='text/html',
             permission='read',
             renderer='templates/site.pt')
def site_get_html(context, request):
    path = os.path.join(
        request.registry.settings['lib-directory'],
        'site.json',
    )
    try:
        fp = io.open(path, 'r', encoding='utf-8')
    except IOError:
        return None
    with fp:
        return {
            'data': json.load(fp)
        }


@view_config(context=Site,
             request_method='GET',
             accept='application/json',
             permission='read',
             renderer='json')
def site_get(context, request):
    path = os.path.join(
        request.registry.settings['lib-directory'],
        'site.json',
    )
    try:
        fp = io.open(path, 'r', encoding='utf-8')
    except IOError:
        return None
    with fp:
        return json.load(fp)


@view_config(context=Site,
             request_method='PUT',
             permission='write')
def site_put(context, request):
    obj = request.json_body
    path = os.path.join(
        request.registry.settings['lib-directory'],
        'site.json',
    )
    if six.PY3:
        fp = io.open(path, 'w', encoding='utf-8')
    else:
        fp = io.open(path, 'wb')
    with fp:
        json.dump(obj, fp)
    return HTTPNoContent()
