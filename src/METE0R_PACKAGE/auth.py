# -*- coding: utf-8 -*-
#
#   METE0R-PROJECT: SOME_DESCRIPTION
#   Copyright (C) 2015-2021 Yoosung Moon <yoosungmoon@naver.com>
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
from urllib.parse import urlencode
from uuid import uuid4
import io
import json
import logging

from pyramid.authentication import AuthTktCookieHelper
from pyramid.authorization import ACLHelper
from pyramid.authorization import Authenticated
from pyramid.authorization import Everyone
from pyramid.httpexceptions import HTTPForbidden
from pyramid.httpexceptions import HTTPFound
from pyramid.httpexceptions import HTTPBadRequest
from pyramid.security import forget
from pyramid.security import remember
from pyramid.session import SignedCookieSessionFactory
from pyramid.view import view_config
import requests


logger = logging.getLogger(__name__)


def includeme(config):
    settings = config.registry.settings

    # TODO: use other session implementation; see
    # https://docs.pylonsproject.org/projects/pyramid/en/latest/narr/sessions.html
    session_factory = SignedCookieSessionFactory(settings["session.secret"])
    config.set_session_factory(session_factory)
    logger.debug("session factory: SignedCookieSessionFactory")

    security_policy = SecurityPolicy(settings["auth_tkt.secret"])
    config.set_security_policy(security_policy)

    google_client_secret_json_file = settings["auth.google.client_secret_json"]
    with io.open(google_client_secret_json_file) as fp:
        google_client_secret = json.load(fp)
        auth_uri = google_client_secret["web"]["auth_uri"]
        token_uri = google_client_secret["web"]["token_uri"]
        client_id = google_client_secret["web"]["client_id"]
        client_secret = google_client_secret["web"]["client_secret"]
        settings["auth.google.auth_uri"] = auth_uri
        settings["auth.google.token_uri"] = token_uri
        settings["auth.google.client_id"] = client_id
        settings["auth.google.client_secret"] = client_secret
    scope = "https://www.googleapis.com/auth/userinfo.email"
    settings["auth.google.scope"] = scope
    config.add_route("login-google", "/login/google")
    config.add_route("login-google-callback", "/login/google/callback")
    config.add_route("logout", "/logout")


class SecurityPolicy:
    def __init__(self, secret):
        self.helper = AuthTktCookieHelper(
            secret=secret,
            timeout=3600,  # 1 hour
            reissue_time=600,  # 10 minutes
            max_age=None,  # does NOT last between browser sessions
        )

    def identity(self, request):
        identity_info = self.helper.identify(request)
        if identity_info is None:
            return None
        userid = identity_info["userid"]

        roles = find_roles(userid, request)
        if roles is not None:
            identity = {
                "userid": userid,
                "roles": roles,
            }
            return identity

    def authenticated_userid(self, request):
        identity = request.identity
        if identity is not None:
            return identity["userid"]

    def permits(self, request, context, permission):
        identity = request.identity
        principals = set([Everyone])
        if identity is not None:
            principals.add(Authenticated)
            principals.add(identity["userid"])
            principals.update(identity["roles"])
        return ACLHelper().permits(context, principals, permission)

    def remember(self, request, userid, **kw):
        return self.helper.remember(request, userid, **kw)

    def forget(self, request, **kw):
        return self.helper.forget(request, **kw)


def find_roles(userid, request):
    return []


@view_config(route_name="login-google")
def login_google(request):
    auth_uri = request.registry.settings["auth.google.auth_uri"]
    client_id = request.registry.settings["auth.google.client_id"]
    login_google_callback = request.route_url("login-google-callback")

    scope = request.registry.settings["auth.google.scope"]
    redirect_uri = request.GET.get("redirect", request.referer or "/")

    state = request.session["auth.google.state"] = uuid4().hex
    request.session["auth.google.redirect"] = redirect_uri

    params = [
        ("scope", scope),
        ("response_type", "code"),
        ("client_id", client_id),
        ("redirect_uri", login_google_callback),
        ("prompt", "select_account"),
        ("access_type", "offline"),
        ("state", state),
    ]
    query_string = urlencode(params, doseq=True)
    url = auth_uri + "?" + query_string
    return HTTPFound(location=url)


@view_config(route_name="login-google-callback")
def login_google_callback(request):
    session_state = request.session.pop("auth.google.state", None)
    request_state = request.GET.get("state")
    if session_state is None or session_state != request_state:
        raise HTTPBadRequest()

    redirect_uri = request.session.pop("auth.google.redirect", None)
    if redirect_uri is None:
        logger.warning("login redirect_uri is not found")
        raise HTTPBadRequest()

    code = request.GET.get("code")
    if code is None or code == "":
        reason = request.GET.get("error", "No reason provided.")  # noqa
        logger.info("Authentication denied: %s", reason)
        raise HTTPForbidden()

    settings = request.registry.settings
    token_uri = settings["auth.google.token_uri"]
    client_id = settings["auth.google.client_id"]
    client_secret = settings["auth.google.client_secret"]

    r = requests.post(
        token_uri,
        {
            "client_id": client_id,
            "client_secret": client_secret,
            "redirect_uri": request.route_url("login-google-callback"),
            "code": code,
            "grant_type": "authorization_code",
        },
    )
    if r.status_code != 200:
        raise ThirdPartyFailure("Status %s: %s" % (r.status_code, r.content))
    token_data = r.json()
    access_token = token_data["access_token"]
    # refresh_token = token_data['refresh_token']

    userinfo_url = (
        "https://www.googleapis.com/oauth2/v1/userinfo?access_token={}".format(
            access_token
        )
    )
    r = requests.get(userinfo_url)
    if r.status_code != 200:
        raise ThirdPartyFailure("Status %s: %s" % (r.status_code, r.content))
    userinfo = r.json()
    # id = userinfo["id"]
    # picture = userinfo["picture"]
    # verified_email = userinfo["verified_email"]
    headers = remember(request, userinfo["email"])
    return HTTPFound(location=redirect_uri, headers=headers)


@view_config(route_name="logout")
def logout(request):
    headers = forget(request)
    return HTTPFound(location=request.referer, headers=headers)


class ThirdPartyFailure(Exception):
    pass
