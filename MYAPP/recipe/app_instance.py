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
import subprocess
import sys


logger = logging.getLogger(__name__)


class AppInstanceRecipe:

    def __init__(self, buildout, name, options):

        bin_directory = buildout['buildout']['bin-directory']
        supervisor = options.get('supervisor')
        app_ini_template = options['app.ini']

        localconfig = '''
[{name}.config]
recipe = mete0r.recipe.localconfig
localconfig.path = {name}.localconfig.json

host = ${{config:host}}
port = ${{config:port}}
        '''.format(name=name)
        buildout.parse(localconfig)
        localconfig = buildout[name + '.config']
        host = localconfig['host']
        port = localconfig['port']

        whoami = '''
[{name}.whoami]
recipe = mete0r.recipe.whoami
        '''
        whoami = whoami.format(name=name)
        buildout.parse(whoami)

        user = buildout[name + '.whoami']['user']
        prefix = buildout['buildout']['directory']
        deployment = '''
[{name}.deployment]
recipe = zc.recipe.deployment
prefix = {prefix}
name = {name}
user = {user}
etc-user = {user}
        '''
        deployment = deployment.format(name=name,
                                       prefix=prefix,
                                       user=user)
        buildout.parse(deployment)
        deployment = buildout[name + '.deployment']

        etc_directory = deployment['etc-directory']
        lib_directory = deployment['lib-directory']
        log_directory = deployment['log-directory']
        run_directory = deployment['run-directory']
        cache_directory = deployment['cache-directory']
        app_ini_path = os.path.join(etc_directory, 'app.ini')
        app_ini_template = app_ini_template.format(
            host=host,
            port=port,
            etc_directory=etc_directory,
            lib_directory=lib_directory,
            log_directory=log_directory,
            run_directory=run_directory,
            cache_directory=cache_directory,
        )

        app_ini = '''
[{name}.app.ini]
recipe = MYAPP:app.ini
path = {path}
template =
{template}
        '''
        app_ini = app_ini.format(name=name,
                                 path=app_ini_path,
                                 template=indent(app_ini_template, ' ' * 8))
        buildout.parse(app_ini)
        app_ini = buildout[name + '.app.ini']

        app = '''
[{name}.script]
recipe = zc.recipe.egg:scripts
eggs = MYAPP
entry-points =
        {name}=MYAPP.recipe.app_instance:main
scripts =
        {name}
arguments = app_ini_path={app_ini_path}, bin_directory={bin_directory}
        '''
        app = app.format(name=name,
                         app_ini_path=repr(app_ini_path),
                         bin_directory=repr(bin_directory))
        buildout.parse(app)
        app = buildout[name + '.script']

        if supervisor:
            # TODO add supervisor config
            app_path = os.path.join(buildout['buildout']['bin-directory'],
                                    name)
            supervisor_conf_dir = buildout[supervisor]['conf-directory']
            supervisor_conf_path = os.path.join(supervisor_conf_dir,
                                                name + '.conf')
            supervisor_conf = '''
[{name}.supervisord.conf]
recipe = collective.recipe.template
output = {output}
mode = 0600
input =
        inline:
        [program:{name}]
        command = {app_path} serve
            '''
            supervisor_conf = supervisor_conf.format(
                name=name,
                app_path=app_path,
                output=supervisor_conf_path
            )
            buildout.parse(supervisor_conf)

    def install(self):
        return ()

    update = install


def main(app_ini_path, bin_directory):
    subcmd = sys.argv[1]
    argv = sys.argv[2:]
    cmd = 'p' + subcmd
    cmd = os.path.join(bin_directory, cmd)
    cmdline = [cmd, app_ini_path] + argv
    return subprocess.call(cmdline)


def indent(text, indent):
    lines = text.split('\n')
    lines = map(lambda line: indent + line, lines)
    lines = '\n'.join(lines)
    return lines
