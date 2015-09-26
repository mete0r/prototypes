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

from zope.interface import implementer

from .interfaces import INavItem
from .interfaces import INavItemCollection
from .interfaces import INavItemSeparator


@implementer(INavItem)
class NavItem(object):

    title = None
    url = None
    current = None


@implementer(INavItemCollection)
class NavItemCollection(object):

    title = None

    def __init__(self):
        self.items = []


@implementer(INavItemSeparator)
class NavItemSeparator(object):
    '''
    '''
