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
from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import Text
from sqlalchemy import Unicode
from sqlalchemy import UniqueConstraint
from sqlalchemy import and_
from sqlalchemy import inspect
from sqlalchemy.exc import NoResultFound

# from sqlalchemy.orm import backref
from sqlalchemy.orm import relationship

# from sqlalchemy.orm.collections import attribute_mapped_collection

from pyramid.httpexceptions import HTTPBadRequest
from pyramid.httpexceptions import HTTPCreated
from pyramid.httpexceptions import HTTPNoContent
from pyramid.view import view_config

from .meta import Base


class Node(Base):
    __tablename__ = "node"
    __table_args__ = (UniqueConstraint("parent_id", "name"),)

    id = Column(Integer, primary_key=True)
    parent_id = Column(ForeignKey("node.id"), index=True)
    name = Column(Unicode(100), nullable=False)
    content = Column(Text, nullable=False)

    parent = relationship(
        "Node",
        remote_side=[id],
        # backref=backref(
        #     "_children",
        #     collection_class=attribute_mapped_collection("name"),
        #     cascade="all",
        # ),
    )

    def __repr__(self):
        return "{}(id={} parent_id={} name={})".format(
            type(self).__name__,
            self.id,
            self.parent_id,
            self.name,
        )

    @property
    def __name__(self):
        return self.name

    @property
    def __parent__(self):
        return self.parent

    def __getitem__(self, name):
        instanceState = inspect(self)
        dbsession = instanceState.session
        q = dbsession.query(Node).filter(
            and_(Node.parent_id == self.id, Node.name == name)
        )
        try:
            return q.one()
        except NoResultFound:
            raise KeyError(name)

    def __iter__(self):
        instanceState = inspect(self)
        dbsession = instanceState.session
        q = dbsession.query(Node.name).filter(Node.parent_id == self.id)
        for (name,) in q:
            yield name


@view_config(
    context=Node,
    request_method="GET",
    accept="application/json",
    renderer="json",
)
def node_json(context, request):
    return {
        "name": context.name,
        "content": context.content,
    }


@view_config(context=Node, request_method="POST")
def node_add(context, request):
    if request.content_type != "application/json":
        raise HTTPBadRequest()
    data = request.json_body
    try:
        name = data["name"]
        content = data["content"]
    except KeyError:
        raise HTTPBadRequest()

    node = Node(name=name, content=content, parent_id=context.id)
    request.dbsession.add(node)
    request.dbsession.flush()

    return HTTPCreated()


@view_config(context=Node, request_method="DELETE")
def node_delete(context, request):
    if context.parent is None:
        raise HTTPBadRequest()
    request.dbsession.delete(context)
    request.dbsession.flush()

    return HTTPNoContent()
