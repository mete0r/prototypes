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
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import os.path

from pyramid.paster import get_appsettings
import alembic
import alembic.config
import alembic.command
import pytest
import transaction
import webtest

from METE0R_PACKAGE import models
from METE0R_PACKAGE.models.meta import Base
from METE0R_PACKAGE.wsgi import app_factory


def pytest_addoption(parser):
    parser.addoption("--ini", action="store", metavar="INI_FILE")


@pytest.fixture(scope="session")
def ini_file(request):
    return os.path.abspath(request.config.option.ini or "testing.ini")


@pytest.fixture(scope="session")
def app_settings(ini_file):
    return get_appsettings(ini_file)


@pytest.fixture(scope="session")
def dbengine(app_settings, ini_file):
    engine = models.get_engine(app_settings)

    alembic_cfg = alembic.config.Config(ini_file)
    Base.metadata.drop_all(bind=engine)
    alembic.command.stamp(alembic_cfg, None, purge=True)

    alembic.command.upgrade(alembic_cfg, "head")

    yield engine

    Base.metadata.drop_all(bind=engine)
    alembic.command.stamp(alembic_cfg, None, purge=True)


@pytest.fixture(scope="session")
def wsgi_app(app_settings, dbengine):
    global_config = {}
    return app_factory(global_config, dbengine=dbengine, **app_settings)


@pytest.fixture
def tm():
    tm = transaction.TransactionManager(explicit=True)
    tm.begin()
    tm.doom()

    yield tm

    tm.abort()


@pytest.fixture
def dbsession(wsgi_app, tm):
    session_factory = wsgi_app.registry["dbsession_factory"]
    return models.get_tm_session(session_factory, tm)


@pytest.fixture
def wsgi_test_app(wsgi_app, tm, dbsession):
    # override request.dbsession and request.tm with our own
    # externally-controlled values that are shared across requests but aborted
    # at the end
    return webtest.TestApp(
        wsgi_app,
        extra_environ={
            "tm.active": True,
            "tm.manager": tm,
            "app.dbsession": dbsession,
        },
    )
