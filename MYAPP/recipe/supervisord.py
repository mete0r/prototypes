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
import os.path


class SupervisordRecipe:

    def __init__(self, buildout, name, options):

        whoami = '''
[supervisord.whoami]
recipe = mete0r.recipe.whoami
        '''.format(name=name)
        buildout.parse(whoami)

        # deployment
        prefix = '${buildout:directory}'
        user = buildout['supervisord.whoami']['user']
        etc_user = buildout['supervisord.whoami']['user']
        buildout.parse('''
[supervisord.deployment]
recipe = zc.recipe.deployment
name = {name}
prefix = {prefix}
user = {user}
etc-user = {etc_user}
        '''.format(name=name,
                   prefix=prefix,
                   user=user,
                   etc_user=etc_user))

        # supervisord.ini
        options['run-directory'] = run_directory = b'${supervisord.deployment:run-directory}'  # noqa
        options['log-directory'] = log_directory = b'${supervisord.deployment:log-directory}'  # noqa
        options['etc-directory'] = etc_directory = b'${supervisord.deployment:etc-directory}'  # noqa
        buildout.parse('''
[supervisord.ini]
recipe = collective.recipe.template
output = {etc_directory}/supervisord.ini
mode = 0600
input =
        inline:
        ; supervisor config file

        [unix_http_server]
        file={run_directory}/supervisor.sock   ; (the path to the socket file)
        chmod=0700                       ; sockef file mode (default 0700)

        [supervisord]
        logfile={log_directory}/supervisord.log ; (main log file;default $CWD/supervisord.log)
        pidfile={run_directory}/supervisord.pid ; (supervisord pidfile;default supervisord.pid)
        childlogdir={log_directory}             ; ('AUTO' child log dir, default $TEMP)

        ; the below section must remain in the config file for RPC
        ; (supervisorctl/web interface) to work, additional interfaces may be
        ; added by defining them in separate rpcinterface: sections
        [rpcinterface:supervisor]
        supervisor.rpcinterface_factory = supervisor.rpcinterface:make_main_rpcinterface

        [supervisorctl]
        serverurl=unix://{run_directory}/supervisor.sock ; use a unix:// URL  for a unix socket

        ; The [include] section can just contain the "files" setting.  This
        ; setting can list multiple files (separated by whitespace or
        ; newlines).  It can also contain wildcards.  The filenames are
        ; interpreted as relative to this file.  Included files *cannot*
        ; include files themselves.

        [include]
        files = {etc_directory}/conf.d/*.conf
        '''.format(name=name,
                   run_directory=run_directory,
                   log_directory=log_directory,
                   etc_directory=etc_directory))
        options['conf-directory'] = os.path.join(etc_directory, b'conf.d')

        ini_path = os.path.join(etc_directory, 'supervisord.ini')
        buildout.parse('''
[sv]
recipe = collective.recipe.template
output = ${{buildout:bin-directory}}/sv
mode = 0700
input =
        inline:
        #!/bin/sh
        app=""
        case "$1" in
        run)
                app="supervisord" ;;
        control)
                app="supervisorctl" ;;
        esac

        [ "$app" = "" ] && {{
                echo "usage: $0 (run|control)"
                exit 1
        }}

        shift
        exec "${{buildout:bin-directory}}/$app" -c "{ini_path}" "$@"
        '''.format(ini_path=ini_path))

    def install(self):
        return tuple()

    def update(self):
        return tuple()
