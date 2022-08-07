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

from pyramid.config import Configurator


def app_factory(global_config, **settings):
    """PasteDeploy app_factory

    see http://pythonpaste.org/deploy/
    """

    with Configurator(
        settings=settings,
    ) as config:
        config.include("pyramid_chameleon")
        config.include(".auth")
        config.include(".locale")
        config.include(".models")
        config.include(".static")
        config.scan()
    return config.make_wsgi_app()
