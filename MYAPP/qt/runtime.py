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
import json
import logging
import os.path
import sys

from PySide.QtCore import Slot
from PySide.QtGui import QApplication
from PySide.QtWebKit import QWebView

from MYAPP.jsonrpc import JsonRpcEndpoint
from MYAPP.jsonrpc import JsonRpcServer


RUNTIME_JS = os.path.join(os.path.dirname(__file__), 'runtime.js')
logger = logging.getLogger(__name__)
endpoint = JsonRpcEndpoint()
export = endpoint.export


class AppRuntime(QApplication):

    def __init__(self, startingUrl, *args, **kwargs):
        super(AppRuntime, self).__init__(*args, **kwargs)

        self.mainView = view = QWebView()
        page = view.page()
        frame = page.mainFrame()

        def onLoadStarted():
            page = view.page()
            frame = page.mainFrame()
            frame.addToJavaScriptWindowObject(u'AppRuntime', self)
            callJS(frame, RUNTIME_JS, True)

        def onLoadProgress(progress):
            logger.debug('loadProgress %s', progress)
            logger.error('url: %s', view.url())

        def onLoadFinished(ok):
            logger.debug('loadFinished %s', ok)
            logger.debug('url: %s', view.url())

            securityOrigin = frame.securityOrigin()
            print securityOrigin.scheme()
            print securityOrigin.host()
            print securityOrigin.port()
            # evalJS('window.Runtime')
            # evalJS('1')
            view.show()

        view.loadStarted.connect(onLoadStarted)
        view.loadProgress.connect(onLoadProgress)
        view.loadFinished.connect(onLoadFinished)
        view.load(startingUrl)

    @property
    def server(self):
        server = getattr(self, '__server', None)
        if not server:
            server = self.__server = JsonRpcServer(endpoint)
        return server

    @Slot(int)
    def exit(self, retval):
        raise SystemExit(retval)

    @Slot(str)
    def pr(self, s):
        try:
            b = s.encode('utf-8')
            sys.stderr.write(b)
        except Exception as e:
            logger.exception(e)

    @Slot(str)
    def println(self, s):
        try:
            b = s.encode('utf-8')
            sys.stdout.write(b)
            sys.stdout.write('\n')
        except Exception as e:
            logger.exception(e)

    @Slot(str, result=str)
    def jsonrpc(self, requestJson):
        request = json.loads(requestJson)
        response = self.server.dispatch(request)
        responseJson = json.dumps(response, indent=2, sort_keys=True)
        return responseJson


def callJS(frame, path, *args):
    with file(path) as f:
        js = f.read().decode('utf-8')
    js = u'(' + js + u')'
    params = u', '.join(json.dumps(x) for x in args)
    params = u'(' + params + u')'
    return evalJS(frame, js + params)


def evalJS(frame, s):
    value = frame.evaluateJavaScript(s)
    logger.debug('evalJS: %r', value)
    return value


@export('console.log')
def console_log(obj, *args):
    logger.info(*args)


@export('console.error')
def console_error(obj, *args):
    logger.error(*args)


@export('console.warn')
def console_warn(obj, *args):
    logger.warning(*args)


@export('console.info')
def console_info(obj, *args):
    logger.info(*args)


@export('console.debug')
def console_debug(obj, *args):
    logger.debug(*args)


@export('console.exception')
def console_exception(obj, *args):
    logger.exception(args[0])
