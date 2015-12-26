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

Just use SignedCookieSessionFactory and don't put large blobs in the session!

with reissue_time=0, manage_accessed() -> changed() will be called in every
request.

'''
from __future__ import absolute_import
from __future__ import unicode_literals
import logging

from pyramid.session import SignedCookieSessionFactory


logger = logging.getLogger(__name__)


def includeme(config):
    settings = config.registry.settings
    secret = settings['session.secret']
    session_factory = SignedCookieSessionFactory(secret)
    config.set_session_factory(session_factory)
