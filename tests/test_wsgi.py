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

# from METE0R_PACKAGE.models.node import Node


def test_wsgi_app_root(wsgi_test_app, dbsession):

    response = wsgi_test_app.get("/", headers=[("Accept", "application/json")])
    assert response.status_code == 200
    assert response.content_type == "application/json"
    assert response.json_body == {
        "name": "",
        "content": "Welcome!",
    }

    response = wsgi_test_app.post_json(
        "/",
        {
            "name": "foo",
            "content": "Foo",
        },
    )
    assert response.status_code == 201  # 201 Created

    response = wsgi_test_app.get("/foo")
    assert response.status_code == 200
    assert response.content_type == "application/json"
    assert response.json_body == {
        "name": "foo",
        "content": "Foo",
    }

    response = wsgi_test_app.post_json(
        "/foo", {"name": "bar", "content": "Bar!"}
    )
    assert response.status_code == 201  # 201 Created

    response = wsgi_test_app.get("/foo/bar")
    assert response.status_code == 200
    assert response.content_type == "application/json"
    assert response.json_body == {
        "name": "bar",
        "content": "Bar!",
    }

    response = wsgi_test_app.post_json(
        "/",
        {
            "name": "hello-world",
            "content": "Hello, World!",
        },
    )
    assert response.status_code == 201  # 201 Created

    response = wsgi_test_app.get("/hello-world")
    assert response.status_code == 200
    assert response.content_type == "application/json"
    assert response.json_body == {
        "name": "hello-world",
        "content": "Hello, World!",
    }

    response = wsgi_test_app.delete("/foo")
    assert response.status_code == 204  # 204 No Content

    response = wsgi_test_app.delete("/", expect_errors=True)
    assert response.status_code == 400  # 400 Bad Request
