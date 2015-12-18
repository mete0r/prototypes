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


class AppIniRecipe:

    def __init__(self, buildout, name, options):

        path = options['path']
        template = options['template']
        template = indent(template, ' '*8)

        section = '''
[{name}.generated]
recipe = collective.recipe.template
output = {path}
mode = 0600
input =
        inline:
{template}
        '''.format(name=name,
                   path=path,
                   template=template)
        buildout.parse(section)

    def install(self):
        return tuple()

    def update(self):
        return tuple()


def indent(text, indent):
    lines = text.split('\n')
    lines = map(lambda line: indent + line, lines)
    lines = '\n'.join(lines)
    return lines
