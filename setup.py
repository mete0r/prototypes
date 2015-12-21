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
from __future__ import with_statement
from contextlib import contextmanager
from fnmatch import fnmatch
import io
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
    with io.open(path, encoding='utf-8') as f:
        return f.read()


@setup_dir
def get_version():
    from MYAPP import __version__
    return __version__


def find_files(relative_to, root_path, exclude):
    found = []
    for directory, subdirs, subfiles in os.walk(root_path):
        for filename in subfiles:
            path = os.path.join(directory, filename)
            path = os.path.relpath(path, relative_to)
            if exclude is None or not exclude(path):
                found.append(path)
    return found


def exclude_bowercomponents_for_install(path):
    pathcomp = path.split(os.path.sep)

    # No npm packages
    if 'node_modules' in pathcomp:
        return True

    # include everything
    return False


def exclude_static_for_install(path):
    dirname = os.path.dirname(path)
    filename = os.path.basename(path)

    # No npm packages
    if 'node_modules' in path.split(os.path.sep):
        return True

    # for bowerstatic
    if filename in ('bower.json', '.bower.json'):
        return False

    # include css/js/fonts
    if fnmatch(filename, '*.css'):
        return False

    if fnmatch(filename, '*.less'):
        return False

    if fnmatch(filename, '*.js'):
        return False

    if dirname == 'static/theme/fonts':
        return False

    # exclude everything
    return True


def alltests():
    import sys
    import unittest
    import zope.testrunner.find
    import zope.testrunner.options
    here = os.path.abspath(os.path.join(os.path.dirname(__file__)))
    args = sys.argv[:]
    defaults = ['--test-path', here]
    options = zope.testrunner.options.get_options(args, defaults)
    suites = list(zope.testrunner.find.find_suites(options))
    return unittest.TestSuite(suites)


tests_require = [
    'zope.testrunner',
    'webtest',
]


setup_info = {
    'name': 'MYAPP',
    'version': get_version(),
    'description': 'SOME_DESCRIPTION',
    'long_description': '\n'.join([readfile('README.rst'),
                                   readfile('CHANGES.rst')]),

    'author': 'mete0r',
    'author_email': 'mete0r@sarangbang.or.kr',
    'license': 'GNU Affero General Public License v3 or later (AGPLv3+)',
    # 'url': 'https://github.com/mete0r/MYAPP',

    'packages': [
        'MYAPP',
        'MYAPP.framework',
        'MYAPP.framework.deform',
        'MYAPP.layouts',
        'MYAPP.panels',
        'MYAPP.recipe',
        'MYAPP.renderers',
        'MYAPP.tests',
        'MYAPP.widgets',
        'MYAPP.widgets.signature',
    ],

    # do not use '.'; just omit to specify setup.py directory
    'package_dir': {
        # '': 'src',
    },

    # 'package_data' specify files to be included in bdist.
    # sdist does additional +/- on these result with MANIFEST.in
    'package_data': {
        'MYAPP': (
            find_files('MYAPP', 'MYAPP/bower_components',
                       exclude_bowercomponents_for_install) +
            find_files('MYAPP', 'MYAPP/static',
                       exclude_static_for_install) +
            find_files('MYAPP', 'MYAPP/templates',
                       None) +
            find_files('MYAPP', 'MYAPP/locale',
                       None) +
            []
        ),
        'MYAPP.framework.deform':
            find_files('MYAPP/framework/deform',
                       'MYAPP/framework/deform/templates',
                       None),
        'MYAPP.recipe': [
            'files/*',
        ],
        # 'MYAPP.tests': [
        #   'files/*',
        # ],
        'MYAPP.widgets.signature': [
            '.bowerrc',
            'bower.json',
            'templates/signature.pt',
            'templates/readonly/signature.pt',
        ],
    },
    'install_requires': [
        'bowerstatic',
        'colander',
        'deform>=2.0a2',
        'pyramid',
        'pyramid_chameleon',
        'pyramid_layout',
        'rfc6266',
        'six',
    ],
    'test_suite': '__main__.alltests',
    'tests_require': tests_require,
    'extras_require': {
        'test': tests_require,
    },
    'entry_points': {
        'console_scripts': [
            'MYAPP = MYAPP.cli:main',
        ],
        'zc.buildout': [
            'default = MYAPP.recipe:Recipe',
            'app.ini = MYAPP.recipe.app_ini:AppIniRecipe',
            'app.instance = MYAPP.recipe.app_instance:AppInstanceRecipe',
            'supervisord = MYAPP.recipe.supervisord:SupervisordRecipe',
        ],
        'zc.buildout.uninstall': [
            'default = MYAPP.recipe:uninstall',
        ],
        'paste.app_factory': [
            'main = MYAPP.wsgi:app_factory',
        ],
    },
    'classifiers': [
        # 'Development Status :: 4 - Beta',
        # 'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)',  # noqa
        # 'Operating System :: OS Independent',
        # 'Programming Language :: Python',
        # 'Programming Language :: Python :: 2.7',
        # 'Programming Language :: Python :: 3.4',
        # 'Programming Language :: Python :: Implementation :: CPython',
    ],
    'keywords': [],
    # 'zip_safe': False,
}


@setup_dir
def main():
    setuptools = import_setuptools()
    setuptools.setup(**setup_info)


if __name__ == '__main__':
    main()
