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


class JsonRpcError(Exception):
    pass


class JsonRpcEndpoint:

    def __init__(self):
        self.exports = {}
        self.exports[()] = {
            'methods': {
                '__exports__': lambda *args: self.get_exports()
            }
        }

    def export(self, method):
        segments = method.split('.')
        object_path = tuple(segments[:-1])
        method_name = segments[-1]

        obj = self.exports.setdefault(object_path, {})
        methods = obj.setdefault('methods', {})

        def decorator(f):
            def wrapper(*args):
                return f(obj, *args)
            methods[method_name] = wrapper
            return f
        return decorator

    def get_exports(self):
        objects = []
        for path in sorted(self.exports):
            obj = self.exports[path]
            objects.append({
                'path': '.'.join(path),
                'methods': list(sorted(obj['methods']))
            })
        return objects

    def dispatch(self, method, params):
        fn = self.resolve(method)
        if not fn:
            raise JsonRpcError('Method not found',
                               -32601,
                               method)

        if len(params) == 0:
            return fn()
        elif isinstance(params, list):
            return fn(*params)
        else:
            return fn(**params)

    def resolve(self, method):
        segments = method.split('.')
        object_path = tuple(segments[:-1])
        method_name = segments[-1]
        obj = self.exports.get(object_path)
        if obj:
            method = obj['methods'].get(method_name)
            return method


class JsonRpcServer:

    logger = logging.getLogger(__name__ + '.JsonRpcServer')

    def __init__(self, endpoint):
        self.endpoint = endpoint

    def dispatch(self, request):
        try:
            request.get('jsonrpc')
            request_id = request.get('id')
            method = request['method']
            params = request.get('params', ())
        except Exception:
            return {
                'error': {
                    'code': -32604,
                    'message': 'Invalid JSON-RPC Response',
                    'data': request
                }
            }

        response = {
            'id': request_id,
        }
        try:
            response['result'] = self.endpoint.dispatch(method, params)
        except JsonRpcError as e:
            message = e.args[0]
            code = e.args[1]
            data = e.args[2]
            response['error'] = {
                'code': code,
                'message': message,
                'data': data
            }
        except Exception as e:
            response['error'] = {
                'code': -32603,  # INTERNAL_ERROR
                'message': str(e).decode('utf-8')
            }
        return response
