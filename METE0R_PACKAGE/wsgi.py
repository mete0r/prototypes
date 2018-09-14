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

from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.config import Configurator
from pyramid.httpexceptions import HTTPClientError
from pyramid.httpexceptions import HTTPFound
from pyramid.httpexceptions import HTTPNoContent
from pyramid.httpexceptions import HTTPServerError
from pyramid.renderers import render_to_response
from pyramid.security import Allow
from pyramid.security import Authenticated
from pyramid.security import Everyone
from pyramid.security import remember
from pyramid.session import SignedCookieSessionFactory
from pyramid.static import ManifestCacheBuster
from pyramid.view import view_config
from pyramid_jwt.policy import JWTAuthenticationPolicy
from pyramid_multiauth import MultiAuthenticationPolicy
from velruse.providers.google_oauth2 import GoogleAuthenticationComplete
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

    google_client_secret_json = settings.get(
        'velruse.google.client_secret.json',
        os.path.join(etc_directory, 'google_client_secret.json'),
    )
    logger.info('loading %s', google_client_secret_json)
    with io.open(google_client_secret_json, 'r', encoding='utf-8') as fp:
        google_client_secret_json = json.load(fp)
        google_client_secret_json = google_client_secret_json['web']
    settings['velruse.google.consumer_key'] = google_client_secret_json[
        'client_id'
    ]
    settings['velruse.google.consumer_secret'] = google_client_secret_json[
        'client_secret'
    ]

    config = Configurator(settings=settings)
    config.set_root_factory(root_factory)
    config.add_translation_dirs(*[
        'locale',
    ])

    authtkt_policy = AuthTktAuthenticationPolicy(
        settings['authtkt.secret']
    )
    config.include('pyramid_jwt')
    jwt_policy = JWTAuthenticationPolicy(
        settings['jwt.private_key'].strip(),
        algorithm=settings.setdefault('jwt.algorithm', 'HS512').strip(),
        expiration=int(settings.setdefault('jwt.expiration', '3600').strip()),
    )
    config.add_request_method(
        jwt_policy.get_claims, 'jwt_claims', reify=True
    )
    policies = [
        authtkt_policy,
        jwt_policy,
    ]
    config.set_authentication_policy(
        MultiAuthenticationPolicy(policies)
    )
    config.set_authorization_policy(
        ACLAuthorizationPolicy()
    )

    session_factory = SignedCookieSessionFactory(
        settings['session.secret'],
    )
    config.set_session_factory(session_factory)

    config.include('velruse.providers.google_oauth2')
    config.add_google_oauth2_login_from_settings()

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


@view_config(context=GoogleAuthenticationComplete)
def google_authentication_complete(context, request):
    logger.debug('profile: %r', context.profile)
    logger.debug('credentials: %r', context.credentials)

    userid = context.profile['preferredUsername']
    headers = remember(request, userid)
    # TODO: profile / credentials
    # TODO: redirect location from session
    location = '/'
    return HTTPFound(location=location, headers=headers)


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
    data = site_get(context, request)
    return {
        'data': data,
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
