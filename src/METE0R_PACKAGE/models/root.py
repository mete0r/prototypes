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
from sqlalchemy import and_
from transaction.interfaces import NoTransaction

from .node import Node


def root_factory(request):
    q = request.dbsession.query(Node).filter(
        and_(Node.parent_id == None, Node.name == "")  # noqa
    )
    try:
        return q.one()
    except NoTransaction:
        # XXX: pshell에서 NoTransaction 예외가 발생한다.
        # XXX: 이 때 다시 시도하면 성공적으로 반환한다.
        return q.one()
