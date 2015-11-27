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
import os.path

from deform import Form
from pkg_resources import resource_filename
from pyramid.threadlocal import get_current_request
from zope.interface import Attribute
from zope.interface import Interface
from zope.interface import implementer


logger = logging.getLogger(__name__)


def includeme(config):
    deform_search_path = DeformSearchPath()
    config.registry.registerUtility(deform_search_path, IDeformSearchPath)

    deform_templates = resource_filename('deform', 'templates')
    override_templates = os.path.join(os.path.dirname(__file__), 'templates')
    deform_search_path.search_path = [
        override_templates,
        deform_templates,
    ]


class IDeformSearchPath(Interface):

    search_path = Attribute('Deform search path tuple.')

    def append(path):
        ''' Append a path to search path '''
    def prepend(path):
        ''' Prepend a path to search path '''


@implementer(IDeformSearchPath)
class DeformSearchPath(object):

    def __init__(self):
        self._search_path = ()

        def translator(term):
            request = get_current_request()
            localizer = request.localizer
            return localizer.translate(term)

        self._translator = translator

    def getSearchPath(self):
        return self._search_path

    def setSearchPath(self, value):
        value = tuple(value)
        self._search_path = value
        Form.set_zpt_renderer(self._search_path, debug=False,
                              translator=self._translator)

    search_path = property(getSearchPath,
                           setSearchPath)

    def prepend(self, path):
        self.search_path = tuple([path]) + self.search_path

    def append(self, path):
        self.search_path += tuple([path])
