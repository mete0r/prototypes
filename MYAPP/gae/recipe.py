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
from cStringIO import StringIO
from argparse import ArgumentParser
import code
import logging
import os.path
import shlex
import sys

import yaml


logger = logging.getLogger(__name__)


class SDKRecipe:

    def __init__(self, buildout, name, options):

        parts_directory = buildout['buildout']['parts-directory']

        sdk_home = os.path.join(parts_directory, name)
        sdk_home = options.setdefault('sdk-home', sdk_home)

        # TODO: parse https://storage.googleapis.com/appengine-sdks
        filename = 'google_appengine_1.9.30.zip'

        section_sdk_zip = '''
[{name}.sdk.zip]
recipe = hexagonit.recipe.download
url = https://storage.googleapis.com/appengine-sdks/featured/{filename}
download-only = true
filename = {filename}
destination = ${{buildout:parts-directory}}

downloaded_path = ${{:destination}}/${{:filename}}
        '''.format(name=name,
                   filename=filename)
        buildout.parse(section_sdk_zip)

        section_sdk = '''
[{name}.sdk]
recipe = hexagonit.recipe.download
url = ${{{name}.sdk.zip:downloaded_path}}
strip-top-level-dir = true
destination = {destination}
        '''.format(name=name,
                   destination=sdk_home)
        buildout.parse(section_sdk)

    def install(self):
        return tuple()

    def update(self):
        return tuple()


class AppYamlRecipe:

    def __init__(self, buildout, name, options):

        app_directory = options['app-directory']
        app_id = options['app-id']
        remote_api = options.get('remote_api')
        version = int(options['version'])

        content = {
            'runtime': 'python27',
            'api_version': 1,
            'threadsafe': True,
            'skip_files': [
                '^(.*/)?#.*#$',
                '^(.*/)?.*~$',
                '^(.*/)?.*\.py[co]$',
                '^(.*/)?.*/RCS/.*$',
            ],
            'version': version,
        }
        template = options.get('template')
        if template:
            f = StringIO()
            f.write(template)
            f.seek(0)
            content.update(yaml.load(f))
        content['application'] = app_id

        if remote_api:
            content.setdefault('builtins', [])
            builtins = content['builtins']
            builtin = builtins_setdefault_remote_api(builtins)
            builtin['remote_api'] = True

        options['path'] = os.path.join(app_directory, b'app.yaml')

        template = yaml.safe_dump(content,
                                  allow_unicode=True,
                                  encoding='utf-8',
                                  default_flow_style=False)
        template = indent(template, ' '*8)
        options['template'] = template.encode('utf-8')

        section = '''
[{name}.generated]
recipe = collective.recipe.template
mode = 0600
output = {output}
input =
        inline:
{template}
        '''.format(name=name,
                   template=template,
                   output=options['path'])
        logger.debug('\n%s', section)
        buildout.parse(section)

    def install(self):
        return tuple()

    def update(self):
        return tuple()


class InstanceRecipe:

    def __init__(self, buildout, name, options):
        bin_directory = buildout['buildout']['bin-directory']
        parts_directory = buildout['buildout']['parts-directory']

        sdk = options['sdk']
        app_id = options.setdefault('app-id', name)
        app_directory = options.setdefault(
            'app-directory', os.path.join(parts_directory, app_id))
        serve_path = options.setdefault(
            'serve-path', os.path.join(bin_directory,
                                       name + b'-serve'))
        remote_api = options.get('remote_api')
        version = options['version']
        supervisord = options.get('supervisord')

        whoami = '''
[{name}.whoami]
recipe = mete0r.recipe.whoami
        '''.format(name=name)
        buildout.parse(whoami)

        deployment = '''
[{name}.deployment]
recipe = zc.recipe.deployment
prefix = ${{buildout:directory}}
name = {name}
user = ${{{name}.whoami:user}}
etc-user = ${{{name}.whoami:user}}
        '''.format(name=name)
        buildout.parse(deployment)

        etc_directory = buildout[name + '.deployment']['etc-directory']
        lib_directory = buildout[name + '.deployment']['lib-directory']

        app_ini = '''
[{name}.app.ini]
recipe = MYAPP:app.ini
path = {path}
template =
{template}
        '''.format(name=name,
                   path=os.path.join(app_directory, 'app.ini'),
                   template=indent(options['app.ini'], ' '*8))
        buildout.parse(app_ini)

        app_yaml = '''
[{name}.app.yaml]
recipe = MYAPP:app.yaml
sdk = {sdk}
app-id = {app_id}
app-directory = {app_directory}
version = {version}
{remote_api}
template =
{template}
        '''.format(name=name,
                   sdk=sdk,
                   app_id=app_id,
                   app_directory=app_directory,
                   template=indent(options['app.yaml'], ' ' * 8),
                   remote_api='remote_api = on' if remote_api else '',
                   version=version)
        buildout.parse(app_yaml)

        upload = '''
[{name}-upload]
recipe = collective.recipe.template
mode = 0700
output = ${{buildout:bin-directory}}/${{:_buildout_section_name_}}
input =
        inline:
        #!/bin/sh
        exec ${{{sdk}:sdk-home}}/appcfg.py update {app_directory} $*
        '''.format(name=name,
                   sdk=sdk,
                   app_directory=app_directory)
        buildout.parse(upload)

        storage_path = lib_directory
        options.setdefault('storage-path', storage_path)
        dev_appserver = '''
[{name}-serve]
recipe = collective.recipe.template
mode = 0700
output = {output}
input =
        inline:
        #!/bin/sh
        exec ${{{sdk}:sdk-home}}/dev_appserver.py\
                --host {host} --port {port}\
                --admin_host {admin_host} --admin_port {admin_port}\
                --storage_path {storage_path}\
                --log_level debug\
                {app_directory}
        '''.format(name=name,
                   sdk=sdk,
                   output=serve_path,
                   app_directory=app_directory,
                   host=options['host'],
                   port=options['port'],
                   admin_host=options['admin-host'],
                   admin_port=options['admin-port'],
                   storage_path=options['storage-path'])
        buildout.parse(dev_appserver)

        testshell = '''
[{name}-testshell]
recipe = MYAPP:testshell
sdk = {sdk}
app-id = {app_id}
app-directory = {app_directory}
        '''.format(name=name,
                   sdk=sdk,
                   app_id=app_id,
                   app_directory=app_directory)
        buildout.parse(testshell)

        if remote_api:
            remoteshell_credentials_path = os.path.join(
                etc_directory, b'remoteshell.serviceaccount.json')
            options.setdefault('remoteshell.serviceaccount.json',
                               remoteshell_credentials_path)
            remoteshell_credentials_path = options[
                'remoteshell.serviceaccount.json'
            ]
            remoteshell = '''
    [{name}-remoteshell]
    recipe = MYAPP:remoteshell
    sdk = {sdk}
    app-id = {app_id}
    app-directory = {app_directory}
    credentials = {credentials}
            '''.format(name=name,
                       sdk=sdk,
                       app_id=app_id,
                       app_directory=app_directory,
                       credentials=remoteshell_credentials_path)
            buildout.parse(remoteshell)

        if supervisord:
            supervisord_conf = '''
[{name}.supervisord.conf]
recipe = collective.recipe.template
output = ${{{supervisord}:conf-directory}}/{name}.conf
mode = 0600
input =
        inline:

        [program:{name}]
        command = {serve_path}

            '''.format(name=name,
                       supervisord=supervisord,
                       serve_path=serve_path)
            buildout.parse(supervisord_conf)

        self.files = []
        files = options.get('files', '')
        files = files.split('\n')
        for filepath in files:
            filename = os.path.basename(filepath)
            dst = os.path.join(app_directory, filename)
            if os.path.exists(dst):
                logger.warning('%s exists', dst)
            else:
                if not os.path.exists(filepath):
                    logger.warning('%s not exists', filepath)
                self.files.append([filepath, dst])

    def install(self):
        for filepath, dst in self.files:
            logger.debug('symlinking %s to %s', filepath, dst)
            os.symlink(filepath, dst)
        return tuple()

    update = install


EXTRA_PATH_LIBS = [
    'lib/antlr3',
    'lib/fancy_urllib',
    'lib/ipaddr',
    'lib/protorpc-1.0',
    'lib/yaml/lib',
    'lib/rsa',
    'lib/pyasn1',
    'lib/pyasn1_modules',
    'lib/httplib2',
    'lib/oauth2client',
    'lib/six',
    'lib/webapp2-2.5.2',
]


class RemoteShellRecipe:

    def __init__(self, buildout, name, options):

        sdk_home = buildout[options['sdk']]['sdk-home']

        arguments = []
        if 'credentials' in options:
            arguments.append('--credentials {}'.format(options['credentials']))

        if 'app-id' in options:
            arguments.append('--app-id {}'.format(options['app-id']))

        if 'app-directory' in options:
            arguments.append(options['app-directory'])

        arguments = ' '.join(arguments)
        arguments = shlex.split(arguments)
        arguments[0:0] = [name]
        arguments = repr(arguments)

        extra_path = map(lambda x: os.path.join(sdk_home, x), EXTRA_PATH_LIBS)
        extra_path.append(sdk_home)
        extra_path = '\n'.join(extra_path)
        extra_path = indent(extra_path, ' ' * 8)

        section = '''
[{name}.generated]
recipe = zc.recipe.egg:scripts
eggs = MYAPP
entry-points =
    {name}=MYAPP.gae.recipe:main_remoteshell
scripts = {name}
arguments = {arguments}
extra-paths =
{extra_path}
        '''.format(name=name,
                   arguments=arguments,
                   extra_path=extra_path)
        buildout.parse(section)

    def install(self):
        return tuple()

    update = install


def main_remoteshell(argv=None):
    argv = argv or sys.argv
    logging.basicConfig(level=logging.DEBUG)

    LIB_DIRECTORIES = [
        'site-packages',
    ]

    parser = ArgumentParser(description='Interactive shell using Remote API.')
    parser.add_argument('app_dir', metavar='APP-DIRECTORY', type=str,
                        help='App directory.')
    parser.add_argument('-A', '--app-id', dest='app_id',
                        help='Google App Engine APP-ID')
    parser.add_argument('-f', '--file', dest='script_file',
                        help='Script file')
    parser.add_argument('--credentials', dest='credentials_file',
                        help='Credentials file')
    args = parser.parse_args(argv[1:])

    from google.appengine.ext.remote_api import remote_api_stub
    from google.appengine.ext import vendor
    import yaml

    app_dir = os.path.abspath(args.app_dir)
    with open(os.path.join(app_dir, 'app.yaml')) as f:
        app_yaml = yaml.load(f)
    app_id = args.app_id or app_yaml['application']

    host = b'{}.appspot.com'.format(app_id)
    path = b'/_ah/remote_api'

    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = args.credentials_file

    remote_api_stub.ConfigureRemoteApiForOAuth(
        host, path, secure=True
    )
    remote_api_stub.MaybeInvokeAuthentication()

    for lib_directory in LIB_DIRECTORIES:
        lib_directory = os.path.join(app_dir, lib_directory)
        lib_directory = os.path.abspath(lib_directory)
        vendor.add(lib_directory)
    sys.path[0:0] = [app_dir, os.getcwd()]

    if args.script_file:
        execfile(args.script_file, {  # noqa
            '__name__': str('__main__'),
        })
    else:
        code.interact(local={
            '__name__': str('__main__'),
        })


class TestShellRecipe:

    def __init__(self, buildout, name, options):

        sdk_home = buildout[options['sdk']]['sdk-home']

        arguments = [name]

        if 'app-id' in options:
            arguments.append('--app-id')
            arguments.append(options['app-id'])
        if 'app-directory' in options:
            arguments.append(options['app-directory'])

        arguments = repr(arguments)

        extra_path = map(lambda x: os.path.join(sdk_home, x), EXTRA_PATH_LIBS)
        extra_path.append(sdk_home)
        extra_path = '\n'.join(extra_path)
        extra_path = indent(extra_path, ' ' * 8)

        section = '''
[{name}.generated]
recipe = zc.recipe.egg:scripts
eggs =
    MYAPP
    Pillow
entry-points =
    {name}=MYAPP.gae.recipe:main_testshell
scripts = {name}
arguments = {arguments}
extra-paths =
{extra_path}
        '''.format(name=name,
                   arguments=arguments,
                   extra_path=extra_path)
        buildout.parse(section)

    def install(self):
        return tuple()

    update = install


def main_testshell(argv=None):
    argv = argv or sys.argv
    logging.basicConfig(level=logging.DEBUG)

    LIB_DIRECTORIES = [
        'site-packages',
    ]

    parser = ArgumentParser(description='Interactive shell using Remote API.')
    parser.add_argument('app_dir', metavar='APP-DIRECTORY', type=str,
                        help='App directory.')
    parser.add_argument('-A', '--app-id', dest='app_id',
                        help='Google App Engine APP-ID')
    parser.add_argument('-f', '--file', dest='script_file',
                        help='Script file')
    args = parser.parse_args(argv[1:])

    from google.appengine.ext.testbed import Testbed
    from google.appengine.ext import vendor
    import yaml

    app_dir = os.path.abspath(args.app_dir)
    with open(os.path.join(app_dir, 'app.yaml')) as f:
        app_yaml = yaml.load(f)
    app_id = args.app_id or app_yaml['application']

    os.environ['APPLICATION_ID'] = app_id

    testbed = Testbed()
    testbed.activate()
    testbed.init_all_stubs()

    for lib_directory in LIB_DIRECTORIES:
        lib_directory = os.path.join(app_dir, lib_directory)
        lib_directory = os.path.abspath(lib_directory)
        vendor.add(lib_directory)
    sys.path[0:0] = [app_dir, os.getcwd()]

    if args.script_file:
        execfile(args.script_file, {  # noqa
            '__name__': str('__main__'),
        })
    else:
        code.interact(local={
            '__name__': str('__main__'),
        })


def builtins_setdefault_remote_api(builtins):
    for builtin in builtins:
        if builtin.get('remote_api'):
            return builtin
    builtin = {
    }
    builtins.append(builtin)
    return builtin


def handlers_setdefault_remote_api(handlers, script):
    for handler in handlers:
        if handler.get('script') == script:
            return handler
    handler = {
        'script': script,
    }
    handlers.append(handler)
    return handler


def indent(text, indent):
    lines = text.split('\n')
    lines = map(lambda line: indent + line, lines)
    lines = '\n'.join(lines)
    return lines
