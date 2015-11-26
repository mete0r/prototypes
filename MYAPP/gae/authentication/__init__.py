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

from pyramid.httpexceptions import HTTPForbidden
from pyramid.httpexceptions import HTTPUnauthorized
from pyramid.interfaces import IAuthenticationPolicy
from pyramid.renderers import render
from pyramid.security import Authenticated
from pyramid.security import Everyone
from zope.interface import implementer


logger = logging.getLogger(__name__)


def includeme(config):
    config.add_request_method(request_login_url, name='get_login_url')
    config.add_request_method(request_logout_url, name='get_logout_url')
    config.add_forbidden_view(forbidden)


def request_login_url(request, redirect_url=None):
    from google.appengine.api import users
    redirect_url = redirect_url or request.url
    login_url = users.create_login_url(redirect_url)
    return login_url


def request_logout_url(request, redirect_url=None):
    from google.appengine.api import users
    redirect_url = redirect_url or request.url
    logout_url = users.create_logout_url(redirect_url)
    return logout_url


class GAEAdministrator(object):
    pass


@implementer(IAuthenticationPolicy)
class GAEAuthenticationPolicy(object):

    def unauthenticated_user(self, request):
        from google.appengine.api import users
        return users.get_current_user()

    def unauthenticated_userid(self, request):
        user = self.unauthenticated_user(request)
        if user is not None:
            return user.user_id()

    def authenticated_user(self, request):
        return self.unauthenticated_user(request)

    def authenticated_userid(self, request):
        user = self.authenticated_user(request)
        if user is not None:
            return user.user_id()

    def effective_principals(self, request):
        from google.appengine.api import users
        principals = [
            Everyone,
        ]
        user = self.authenticated_user(request)
        if user is not None:
            principals.append(Authenticated)
        if users.is_current_user_admin():
            principals.append(GAEAdministrator)
        return principals

    def remember(self, request, principal, **kw):
        return ()

    def forget(self, request):
        return ()


def forbidden(request):
    if request.authenticated_userid:
        rendered = render('templates/forbidden.pt', {
        }, request)
        return HTTPForbidden(body=rendered)

    rendered = render('templates/unauthorized.pt', {
    }, request)
    return HTTPUnauthorized(body=rendered)
