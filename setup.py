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
from __future__ import with_statement
from contextlib import contextmanager
import os.path


def setup_dir(f):
    ''' Decorate f to run inside the directory where setup.py resides.
    '''
    setup_dir = os.path.dirname(os.path.abspath(__file__))

    def wrapped(*args, **kwargs):
        with chdir(setup_dir):
            return f(*args, **kwargs)

    return wrapped


@contextmanager
def chdir(new_dir):
    old_dir = os.path.abspath(os.curdir)
    os.chdir(new_dir)
    try:
        yield
    finally:
        os.chdir(old_dir)


@setup_dir
def import_setuptools():
    try:
        import setuptools
        return setuptools
    except ImportError:
        pass

    import ez_setup
    ez_setup.use_setuptools()
    import setuptools
    return setuptools


@setup_dir
def readfile(path):
    with file(path) as f:
        return f.read()


setup_info = {
    'name': 'MYAPP',
    'version': readfile('VERSION.txt').strip(),
    'description': 'SOME_DESCRIPTION',
    'long_description': readfile('README.rst') + readfile('CHANGES.rst'),

    'author': 'mete0r',
    'author_email': 'mete0r@sarangbang.or.kr',
    'license': 'GNU Affero General Public License v3 or later (AGPLv3+)',
    # 'url': 'https://github.com/mete0r/MYAPP',

    'packages': [
        'MYAPP'
    ],
    'package_dir': {'': '.'},
    'install_requires': [
        'logutils',
    ],
    'entry_points': {
        'console_scripts': ['MYAPP = MYAPP.cli:main'],
        'gui_scripts': ['QMYAPP = MYAPP.qt:main'],
        'zc.buildout': ['default = MYAPP.recipe:Recipe'],
        'zc.buildout.uninstall': ['default = MYAPP.recipe:uninstall'],
        'paste.app_factory': ['main = MYAPP.wsgi:app_factory'],
    }
}


@setup_dir
def main():
    setuptools = import_setuptools()
    setuptools.setup(**setup_info)


if __name__ == '__main__':
    main()
