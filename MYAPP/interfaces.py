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

from zope.interface import Attribute
from zope.interface import Interface


class INavItem(Interface):

    title = Attribute('Title')
    url = Attribute('URL')
    current = Attribute('Currently active.')


class INavItemCollection(Interface):

    title = Attribute('Title')
    items = Attribute('Iterable of INavItem')


class INavItemSeparator(Interface):
    pass


class IMailer(Interface):

    def send(mime_message):
        ''' Send a MIME message. '''


class IViewable(Interface):
    '''
    '''


class IDownloadable(Interface):
    '''
    '''

    content_type = Attribute('HTTP Content-Type')
    content_filename = Attribute('Filename for Content-Disposition header')
    content_bytes = Attribute('content bytes')


class IUploadable(Interface):
    '''
    '''


class IUpload(Interface):
    '''
    '''


class IAddable(Interface):

    def getAdder(typename):
        '''
        '''


class IAdd(Interface):

    schema = Attribute('Colander Schema.')
    appstruct = Attribute('Initial appstruct. Read-only.')

    def __call__(appstruct):
        '''
        '''


class IEditable(Interface):
    pass


class IEdit(Interface):

    schema = Attribute('Colander Schema.')
    appstruct = Attribute('Colander appstruct')


class IDeletable(Interface):
    pass


class INode(IViewable, IDeletable):
    pass


class IFolder(INode, IAddable, IEditable):

    children = Attribute('Children iterable.')


class IDocument(INode, IEditable):

    title = Attribute('Title.')
    html_content = Attribute('HTML Content.')
