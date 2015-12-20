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
import logging

from pyramid.httpexceptions import HTTPFound
from pyramid.response import Response
from pyramid.view import view_config
from deform import Form
from deform import ValidationFailure
import colander
import deform
import rfc6266

from .interfaces import IViewable
from .interfaces import IAddable
from .interfaces import IAdd
from .interfaces import IEditable
from .interfaces import IEdit
from .interfaces import IDeletable
from .interfaces import IDownloadable
from .interfaces import IUploadable
from .interfaces import IUpload
from .widgets import deferred_fileupload_widget


logger = logging.getLogger(__name__)


def includeme(config):
    config.scan('.views')


@view_config(context=IViewable,
             renderer='templates/node_view.pt',
             permission='view')
def node_view(context, request):
    return {
    }


@view_config(context=IDownloadable, name='download',
             request_method='GET',
             permission='download')
def node_download(context, request):
    content_type = context.content_type
    content_bytes = context.content_bytes
    content_disposition = rfc6266.build_header(context.content_filename)
    response = Response(content_bytes,
                        headers={
                            b'content-type': bytes(content_type),
                            b'content-disposition': bytes(content_disposition),
                        })
    return response


class UploadFiles(colander.SequenceSchema):
    file = colander.SchemaNode(deform.FileData(),
                               widget=deferred_fileupload_widget)


class UploadSchema(colander.MappingSchema):
    files = UploadFiles()


@view_config(context=IUploadable, name='upload',
             renderer='templates/node_upload.pt',
             permission='upload')
def node_upload(context, request):
    schema = UploadSchema()
    schema = schema.bind()
    form = Form(schema, buttons=('upload',))
    request.include_deform_widget(form)
    return {
        'form': form.render(),
    }


@view_config(context=IUploadable, name='upload',
             request_method='POST',
             renderer='templates/node_upload.pt',
             permission='upload')
def node_upload_post(context, request):
    schema = UploadSchema()
    schema = schema.bind()
    form = Form(schema, buttons=('upload',))
    upload = request.registry.getAdapter(context, IUpload)
    if 'upload' in request.POST:
        controls = request.POST.items()
        try:
            appstruct = form.validate(controls)
        except ValidationFailure as e:
            request.include_deform_widget(form)
            return {
                'form': e.render(),
            }
        else:
            for filedata in appstruct['files']:
                upload.upload(filedata)
            location = request.resource_url(context)
    else:
        location = request.resource_url(context, '@@upload')
    return HTTPFound(location=location)


@view_config(context=IAddable, name='add',
             renderer='templates/node_add.pt',
             permission='add')
def node_add(context, request):
    typename = request.GET['type']
    add = request.registry.getAdapter(context, IAdd, typename)
    form = Form(add.schema.bind(), buttons=('add',))
    request.include_deform_widget(form)
    return {
        'form': form.render(),
    }


@view_config(context=IAddable, name='add',
             request_method='POST',
             renderer='templates/node_add.pt',
             permission='add')
def node_add_post(context, request):
    typename = request.GET['type']
    add = request.registry.getAdapter(context, IAdd, typename)
    form = Form(add.schema.bind(), buttons=('add',))
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
             renderer='templates/node_edit.pt',
             permission='edit')
def node_edit(context, request):
    edit = request.registry.getAdapter(context, IEdit)
    form = Form(edit.schema.bind(), buttons=('submit',))
    request.include_deform_widget(form)
    return {
        'form': form.render(edit.appstruct),
    }


@view_config(context=IEditable, name='edit',
             request_method='POST',
             renderer='templates/node_edit.pt',
             permission='edit')
def node_edit_post(context, request):
    edit = request.registry.getAdapter(context, IEdit)
    form = Form(edit.schema.bind(), buttons=('submit',))
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
             renderer='templates/node_delete.pt',
             permission='delete')
def node_delete(context, request):
    return {
    }


@view_config(context=IDeletable, name='delete',
             request_method='POST',
             permission='delete')
def node_delete_post(context, request):
    parent = context.__parent__
    del parent[context.__name__]
    location = request.resource_url(parent)
    return HTTPFound(location=location)
