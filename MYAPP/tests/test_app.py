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

from unittest import TestCase
import os.path
import shutil


class AppTest(TestCase):

    def setUp(self):
        name = self.id()
        if os.path.exists(name):
            shutil.rmtree(name)
        os.mkdir(name)

    def make_one(self):
        from webtest.app import TestApp
        from ..wsgi import app_factory

        app = app_factory({}, **{
            'session.secret': 'not-so-secret',
        })
        app = TestApp(app)
        return app

    def test_root(self):
        app = self.make_one()
        resp = app.get('/')
        self.assertEquals(resp.status, '200 OK')
