# -*- coding: utf-8 -*-
#
#   MYAPP : SOME_DESCRIPTION
#   Copyright (C) 2014 mete0r <mete0r@sarangbang.or.kr>
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
import logging
import os.path
import sys

from logutils.colorize import ColorizingStreamHandler

from MYAPP.qt.runtime import AppRuntime

HTML5_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'html5')
INDEX_HTML = os.path.join(HTML5_DIR, 'index.html')

logger = logging.getLogger(__name__)


def main():
    logging.getLogger().addHandler(ColorizingStreamHandler())
    logging.getLogger('MYAPP').setLevel(logging.DEBUG)

    runtime = AppRuntime(INDEX_HTML, sys.argv)
    runtime.exec_()
