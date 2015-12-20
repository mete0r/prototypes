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

from google.appengine.ext import ndb

from ..ndb import Session
from .document import Document
from .folder import Folder


logger = logging.getLogger(__name__)


def includeme(config):
    config.scan()


def root_factory(request):
    session = Session()
    root_key = ndb.Key(Folder, 'ROOT')
    try:
        root = session[root_key]
    except KeyError:
        root = Folder()
        session[root_key] = root
        root['index'] = Document(title='Index',
                                 html_content='<p>This is folder index.</p>')
        root['foo'] = Document(title='Foo',
                               html_content='<p>Foo content</p>')
        root['folder'] = folder = Folder(title='Folder')
        folder['bar'] = Document(title='Bar',
                                 html_content='<p>Bar content</p>')
        session.flush()

    request.ndb_session = session
    request.add_finished_callback(onFinished)
    return root


def onFinished(request):
    flushed = request.ndb_session.flush()
    for x in flushed:
        logger.info('flushed: %s', x)
