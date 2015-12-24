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
'''

Session implementation based on dogpile.cache.

TODO: currently session is always accessed (for flash messages by default
layout), so cookie/session entry in the cache is always updated. Optimize it.
'''
from __future__ import absolute_import
from __future__ import unicode_literals
from base64 import urlsafe_b64encode
import binascii
import hashlib
import logging
import os
import time


from dogpile.cache import make_region
from dogpile.cache.api import NO_VALUE
from pyramid.compat import bytes_
from pyramid.compat import native_
from pyramid.compat import text_
from pyramid.compat import PY3
from pyramid.interfaces import ISessionFactory
from pyramid.interfaces import ISession
from pyramid.session import PickleSerializer
from pyramid.session import SignedSerializer
from pyramid.session import manage_accessed
from pyramid.session import manage_changed
from zope.interface import implementer
from zope.interface import directlyProvides


logger = logging.getLogger(__name__)


def includeme(config):
    settings = config.registry.settings
    Session.configure_from_settings(settings)
    config.set_session_factory(Session)


@implementer(ISession)
class Session(dict):
    """ Dictionary-like session object """

    # dirty flag
    _dirty = False

    @classmethod
    def configure_from_settings(cls, settings):
        cache_region = make_region(name='session')
        expiration_time = settings.get('session.expiration_time')
        if expiration_time is not None:
            expiration_time = int(expiration_time)
        backend = settings['session.backend']
        cache_region.configure(backend=backend,
                               expiration_time=expiration_time,
                               _config_argument_dict=settings,
                               _config_prefix='session.backend.arguments.')

        secret = settings['session.secret']
        salt = 'pyramid.session.'
        hashalg = 'sha512'
        serializer = PickleSerializer()
        signed_serializer = SignedSerializer(secret,
                                             salt,
                                             hashalg,
                                             serializer=serializer)
        hasher = StateHasher(secret)
        state_storage = StateStorage(cache_region=cache_region,
                                     serializer=serializer,
                                     hasher=hasher)

        cls.configure(state_storage=state_storage,
                      cookie_serializer=signed_serializer)

    @classmethod
    def configure(cls,
                  state_storage,
                  cookie_serializer,
                  cookie_name='session',
                  max_age=None,
                  path='/',
                  domain=None,
                  secure=False,
                  httponly=False,
                  set_on_exception=True,
                  timeout=1200,
                  reissue_time=0):
        cls.state_storage = state_storage
        cls.cookie_serializer = cookie_serializer

        cls._cookie_name = cookie_name
        cls._cookie_max_age = max_age
        cls._cookie_path = path
        cls._cookie_domain = domain
        cls._cookie_secure = secure
        cls._cookie_httponly = httponly
        cls._cookie_on_exception = set_on_exception
        cls._timeout = timeout
        cls._reissue_time = reissue_time

    def __init__(self, request):
        self.request = request

        now = time.time()
        created = renewed = now
        new = True
        value = None
        state = {}
        cookieval = request.cookies.get(self._cookie_name)
        if cookieval is not None:
            try:
                value = self.cookie_serializer.loads(bytes_(cookieval))
            except Exception:
                # the cookie failed to deserialize, dropped
                value = None

        if value is not None:
            try:
                # since the value is not necessarily signed, we have
                # to unpack it a little carefully
                rval, cval, skey = value
                renewed = float(rval)
                created = float(cval)
                state = self.state_storage.load(skey)
                new = False
            except (TypeError, ValueError, KeyError):
                # value failed to unpack properly or renewed was not
                # a numeric type so we'll fail deserialization here
                state = {}

        if self._timeout is not None:
            if now - renewed > self._timeout:
                # expire the session because it was not renewed
                # before the timeout threshold
                state = {}

        self.created = created
        self.accessed = renewed
        self.renewed = renewed
        self.new = new
        dict.__init__(self, state)

    # ISession methods
    def changed(self):
        if not self._dirty:
            self._dirty = True

            def set_cookie_callback(request, response):
                self._set_cookie(response)
                self.request = None  # explicitly break cycle for gc
            self.request.add_response_callback(set_cookie_callback)

    def invalidate(self):
        self.clear()  # XXX probably needs to unset cookie

    # non-modifying dictionary methods
    get = manage_accessed(dict.get)
    __getitem__ = manage_accessed(dict.__getitem__)
    items = manage_accessed(dict.items)
    values = manage_accessed(dict.values)
    keys = manage_accessed(dict.keys)
    __contains__ = manage_accessed(dict.__contains__)
    __len__ = manage_accessed(dict.__len__)
    __iter__ = manage_accessed(dict.__iter__)

    if not PY3:
        iteritems = manage_accessed(dict.iteritems)
        itervalues = manage_accessed(dict.itervalues)
        iterkeys = manage_accessed(dict.iterkeys)
        has_key = manage_accessed(dict.has_key)

    # modifying dictionary methods
    clear = manage_changed(dict.clear)
    update = manage_changed(dict.update)
    setdefault = manage_changed(dict.setdefault)
    pop = manage_changed(dict.pop)
    popitem = manage_changed(dict.popitem)
    __setitem__ = manage_changed(dict.__setitem__)
    __delitem__ = manage_changed(dict.__delitem__)

    # flash API methods
    @manage_changed
    def flash(self, msg, queue='', allow_duplicate=True):
        storage = self.setdefault('_f_' + queue, [])
        if allow_duplicate or (msg not in storage):
            storage.append(msg)

    @manage_changed
    def pop_flash(self, queue=''):
        storage = self.pop('_f_' + queue, [])
        return storage

    @manage_accessed
    def peek_flash(self, queue=''):
        storage = self.get('_f_' + queue, [])
        return storage

    # CSRF API methods
    @manage_changed
    def new_csrf_token(self):
        token = text_(binascii.hexlify(os.urandom(20)))
        self['_csrft_'] = token
        return token

    @manage_accessed
    def get_csrf_token(self):
        token = self.get('_csrft_', None)
        if token is None:
            token = self.new_csrf_token()
        return token

    # non-API methods
    def _set_cookie(self, response):
        if not self._cookie_on_exception:
            exception = getattr(self.request, 'exception', None)
            # dont set a cookie during exceptions
            if exception is not None:
                return False

        state = dict(self)
        key = self.state_storage.add(state)
        cookieval = native_(self.cookie_serializer.dumps(
            (self.accessed, self.created, key)
            ))
        if len(cookieval) > 4064:
            raise ValueError(
                'Cookie value is too long to store (%s bytes)' %
                len(cookieval)
                )
        response.set_cookie(
            self._cookie_name,
            value=cookieval,
            max_age=self._cookie_max_age,
            path=self._cookie_path,
            domain=self._cookie_domain,
            secure=self._cookie_secure,
            httponly=self._cookie_httponly,
            )
        return True


directlyProvides(Session, ISessionFactory)


class StateStorage(object):

    def __init__(self, cache_region, serializer, hasher):
        self.cache_region = cache_region
        self.serializer = serializer
        self.hasher = hasher

    def add(self, state):
        serialized_state = self.serializer.dumps(state)
        hashed = self.hasher(serialized_state)
        logger.debug('save session state for %s: %r', hashed, state)
        self.cache_region.set(hashed, serialized_state)
        return hashed

    def load(self, hashed):
        serialized_state = self.cache_region.get(hashed)
        if serialized_state == NO_VALUE:
            logger.debug('load session state for %s: NOT FOUND', hashed)
            raise KeyError(hashed)
        try:
            state = self.serializer.loads(serialized_state)
        except Exception as e:
            logger.exception(e)
            raise KeyError(hashed)
        logger.debug('load session state for %s: %r', hashed, state)
        return state


class StateHasher(object):

    def __init__(self, secret):
        self.secret = secret

    def __call__(self, content):
        h = hashlib.sha1()
        h.update(self.secret)
        h.update(content)
        digested = h.digest()
        hashed = urlsafe_b64encode(digested)
        return hashed
