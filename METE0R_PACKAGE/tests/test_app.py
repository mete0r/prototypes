# -*- coding: utf-8 -*-
#
#   METE0R-PROJECT: SOME_DESCRIPTION
#   Copyright (C) 2015-2017 mete0r <mete0r@sarangbang.or.kr>
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
from __future__ import print_function
from __future__ import unicode_literals
from datetime import datetime
from functools import wraps
from unittest import TestCase
import logging
import os.path
import sys

from paste.deploy import appconfig
from webtest import TestApp
import jwt

from .utils import isolated_directory


def app_factory(test_fn):

    @wraps(test_fn)
    def wrapper(self, isolated_directory):
        lib_directory = os.path.join(isolated_directory, 'lib')
        run_directory = os.path.join(isolated_directory, 'run')
        cache_directory = os.path.join(isolated_directory, 'cache')
        os.makedirs(lib_directory)
        os.makedirs(run_directory)
        os.makedirs(cache_directory)

        from ..wsgi import app_factory
        app_ini = os.path.join(
            sys.prefix, 'development.ini',
        )

        config_uri = 'config:{}'.format(app_ini)
        config = appconfig(config_uri)

        global_config = config.global_conf
        settings = config.local_conf
        settings['lib-directory'] = lib_directory
        settings['run-directory'] = run_directory
        settings['cache-directory'] = cache_directory

        app = app_factory(global_config, **settings)
        return test_fn(self, app)
    return wrapper


class AppTest(TestCase):

    @property
    def logger(self):
        name = self.id()
        return logging.getLogger(name)

    @isolated_directory
    @app_factory
    def test_root(self, app):
        testapp = TestApp(app)

        r = testapp.get('/')
        self.assertEquals(None, r.json)

        r = testapp.put_json('/', 'Hello', status=403)

        token = jwt.encode({
            'sub': 'admin',
            'iat': datetime.utcnow(),
        }, app.registry.settings['jwt.private_key'], algorithm='HS512')
        token = token.decode('ascii')

        testapp.authorization = ('JWT', token)
        r = testapp.put_json('/', 'Hello')

        r = testapp.get('/')
        self.assertEquals('Hello', r.json)
