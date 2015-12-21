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

from pyramid.location import lineage
from pyramid_layout.layout import layout_config

from ..bowerstatic import bootstrap_css
from ..bowerstatic import bootstrap_js

from ..nav import NavItem
from ..nav import NavItemCollection


logger = logging.getLogger(__name__)


@layout_config(template='../templates/layouts/default.pt')
class DefaultLayout(object):

    brand_name = 'MYAPP'

    def __init__(self, context, request):
        self.context = context
        self.request = request
        request.include(bootstrap_css)
        request.include(bootstrap_js)
        self.use_deform = False

    @property
    def navbar_title(self):
        if self.is_root:
            return self.brand_name
        return self.title

    @property
    def title(self):
        return self.context.__name__

    @property
    def is_root(self):
        return self.context.__parent__ is None

    @property
    def nav(self):
        url = self.request.resource_url(self.context)

        nav = NavItemCollection()
        items = lineage(self.context)
        items = list(items)
        items = items[:-1]
        items = reversed(items)
        for item in items:
            navitem_dropdown = NavItemCollection()
            navitem_dropdown.title = ''
            for sibling in item.__parent__.children:
                navitem = NavItem()
                navitem.title = sibling.__name__
                navitem.url = self.request.resource_url(sibling)
                navitem.current = navitem.url == url
                navitem_dropdown.items.append(navitem)
            nav.items.append(navitem_dropdown)

            navitem = NavItem()
            navitem.title = item.__name__
            navitem.url = self.request.resource_url(item)
            navitem.current = navitem.url == url
            nav.items.append(navitem)
        return nav
