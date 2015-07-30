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

from pyramid.httpexceptions import HTTPFound
from pyramid.view import view_config
from deform import Form
from deform import ValidationFailure

from .interfaces import IViewable
from .interfaces import IAddable
from .interfaces import IAdd
from .interfaces import IEditable
from .interfaces import IEdit
from .interfaces import IDeletable


@view_config(context=IViewable,
             renderer='templates/node_view.pt')
def node_view(context, request):
    return {
    }


@view_config(context=IAddable, name='add',
             renderer='templates/node_add.pt')
def node_add(context, request):
    typename = request.subpath[0]
    add = request.registry.getAdapter(context, IAdd, typename)
    form = Form(add.schema, buttons=('add',))
    request.include_deform_widget(form)
    return {
        'form': form.render(),
    }


@view_config(context=IAddable, name='add',
             request_method='POST',
             renderer='templates/node_add.pt')
def node_add_post(context, request):
    typename = request.subpath[0]
    add = request.registry.getAdapter(context, IAdd, typename)
    form = Form(add.schema, buttons=('add',))
    if 'add' in request.POST:
        controls = request.POST.items()
        try:
            appstruct = form.validate(controls)
        except ValidationFailure as e:
            request.include_deform_widget(form)
            return {
                'form': e.render(),
            }
        else:
            added = add(appstruct)
            location = request.resource_url(added)
    else:
        location = request.resource_url(context, '@@add', typename)
    return HTTPFound(location=location)


@view_config(context=IEditable, name='edit',
             renderer='templates/node_edit.pt')
def node_edit(context, request):
    edit = request.registry.getAdapter(context, IEdit)
    form = Form(edit.schema, buttons=('submit',))
    request.include_deform_widget(form)
    return {
        'form': form.render(edit.appstruct),
    }


@view_config(context=IEditable, name='edit',
             request_method='POST',
             renderer='templates/node_edit.pt')
def node_edit_post(context, request):
    edit = request.registry.getAdapter(context, IEdit)
    form = Form(edit.schema, buttons=('submit',))
    if 'submit' in request.POST:
        controls = request.POST.items()
        try:
            appstruct = form.validate(controls)
        except ValidationFailure as e:
            request.include_deform_widget(form)
            return {
                'form': e.render(),
            }
        else:
            edit.appstruct = appstruct
            location = request.resource_url(context)
    else:
        location = request.resource_url(context, '@@edit')
    return HTTPFound(location=location)


@view_config(context=IDeletable, name='delete',
             renderer='templates/node_delete.pt')
def node_delete(context, request):
    return {
    }


@view_config(context=IDeletable, name='delete',
             request_method='POST')
def node_delete_post(context, request):
    parent = context.__parent__
    del parent[context.__name__]
    location = request.resource_url(parent)
    return HTTPFound(location=location)
