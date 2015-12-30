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
from deform import Button
from deform import Form
from deform import ValidationFailure
import colander
import deform
import rfc6266

from ..i18n import _
from ..i18n import translate
from ..interfaces import IAddable
from ..interfaces import IAdd
from ..interfaces import IEditable
from ..interfaces import IEdit
from ..interfaces import IDeletable
from ..interfaces import IDownloadable
from ..interfaces import IUploadable
from ..interfaces import IUpload
from ..widgets import deferred_fileupload_widget
from .csrf import CSRF_TOKEN_NAME
from .csrf import CSRF_TOKEN_SCHEMA


logger = logging.getLogger(__name__)


MSG_ADD = _('Add')
MSG_SAVE = _('Save')
MSG_UPLOAD = _('Upload')


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
             renderer='../templates/views/action/node_upload.pt',
             permission='upload')
def node_upload(context, request):
    schema = UploadSchema()
    schema = schema.bind()
    schema.add(CSRF_TOKEN_SCHEMA)
    buttons = (
        Button('upload', translate(MSG_UPLOAD, request)),
    )
    form = Form(schema, buttons=buttons)
    request.include_deform_widget(form)
    appstruct = {}
    appstruct[CSRF_TOKEN_NAME] = request.session.new_csrf_token()
    return {
        'form': form.render(appstruct),
    }


@view_config(context=IUploadable, name='upload',
             request_method='POST',
             check_csrf=CSRF_TOKEN_NAME,
             renderer='../templates/views/action/node_upload.pt',
             permission='upload')
def node_upload_post(context, request):
    schema = UploadSchema()
    schema = schema.bind()
    buttons = (
        Button('upload', translate(MSG_UPLOAD, request)),
    )
    form = Form(schema, buttons=buttons)
    upload = request.registry.getMultiAdapter((context, request), IUpload)
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
             renderer='../templates/views/action/node_add.pt',
             permission='add')
def node_add(context, request):
    typename = request.GET['type']
    buttons = (
        Button('add', translate(MSG_ADD, request)),
    )
    add = request.registry.getMultiAdapter((context, request), IAdd, typename)
    schema = add.schema.bind()
    schema.add(CSRF_TOKEN_SCHEMA)
    form = Form(schema, buttons=buttons)
    appstruct = add.appstruct
    appstruct[CSRF_TOKEN_NAME] = request.session.new_csrf_token()
    request.include_deform_widget(form)
    return {
        'form': form.render(appstruct),
    }


@view_config(context=IAddable, name='add',
             request_method='POST',
             check_csrf=CSRF_TOKEN_NAME,
             renderer='../templates/views/action/node_add.pt',
             permission='add')
def node_add_post(context, request):
    typename = request.GET['type']
    buttons = (
        Button('add', translate(MSG_ADD, request)),
    )
    add = request.registry.getMultiAdapter((context, request), IAdd, typename)
    form = Form(add.schema.bind(), buttons=buttons)
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
             renderer='../templates/views/action/node_edit.pt',
             permission='edit')
def node_edit(context, request):
    edit = request.registry.getMultiAdapter((context, request), IEdit)
    buttons = (
        Button('save', translate(MSG_SAVE, request)),
    )
    schema = edit.schema.bind()
    schema.add(CSRF_TOKEN_SCHEMA)
    form = Form(schema, buttons=buttons)
    request.include_deform_widget(form)
    appstruct = edit.appstruct
    appstruct[CSRF_TOKEN_NAME] = request.session.new_csrf_token()
    return {
        'form': form.render(appstruct),
    }


@view_config(context=IEditable, name='edit',
             request_method='POST',
             check_csrf=CSRF_TOKEN_NAME,
             renderer='../templates/views/action/node_edit.pt',
             permission='edit')
def node_edit_post(context, request):
    edit = request.registry.getMultiAdapter((context, request), IEdit)
    buttons = (
        Button('save', translate(MSG_SAVE, request)),
    )
    form = Form(edit.schema.bind(), buttons=buttons)
    if 'save' in request.POST:
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
             renderer='../templates/views/action/node_delete.pt',
             permission='delete')
def node_delete(context, request):
    return {
        'csrf_token_name': CSRF_TOKEN_NAME,
        'csrf_token_value': request.session.new_csrf_token(),
    }


@view_config(context=IDeletable, name='delete',
             request_method='POST',
             check_csrf=CSRF_TOKEN_NAME,
             permission='delete')
def node_delete_post(context, request):
    parent = context.__parent__
    del parent[context.__name__]
    location = request.resource_url(parent)
    return HTTPFound(location=location)
