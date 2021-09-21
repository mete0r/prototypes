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
from pyramid.view import view_config


class Root:
    __name__ = ""
    __parent__ = None


def root_factory(request):
    return Root()


@view_config(context=Root, accept="application/json", renderer="json")
def root_json(context, request):
    return None


@view_config(
    context=Root,
    accept="text/html",
    renderer="METE0R_PACKAGE:templates/root.pt",
)
def root_html(context, request):
    return {
        "title": "Welcome!",
    }
