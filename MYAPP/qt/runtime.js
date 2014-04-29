//
//  MYAPP : SOME_DESCRIPTION
//  Copyright (C) 2014 mete0r <mete0r@sarangbang.or.kr>
//
//  This program is free software: you can redistribute it and/or modify
//  it under the terms of the GNU Affero General Public License as published by
//  the Free Software Foundation, either version 3 of the License, or
//  (at your option) any later version.
//
//  This program is distributed in the hope that it will be useful,
//  but WITHOUT ANY WARRANTY; without even the implied warranty of
//  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
//  GNU Affero General Public License for more details.
//
//  You should have received a copy of the GNU Affero General Public License
//  along with this program.  If not, see <http://www.gnu.org/licenses/>.
//
function() {
  'use strict';

  function JsonRpcTransport(send) {
    this._send = send;
  }

  JsonRpcTransport.prototype.send = function sendRequest(request) {
    var requestJson = JSON.stringify(request);
    // R.println('sending request: ' + requestJson);
    var responseJson = this._send(requestJson);
    // R.println('receiving response: ' + responseJson);
    var response = JSON.parse(responseJson);
    return response;
  };

  function JsonRpcClient(transport) {
    this.transport = transport;
    this.id = 0;
  }

  JsonRpcClient.prototype.invoke = function invoke(method, params) {
    var request = {
      jsonrpc: '2.0',
      id: ++this.id,
      method: method,
      params: params
    };

    var response = this.transport.send(request);
    if (response.result !== undefined) {
      return response.result;
    } else if (response.error !== undefined) {
      var e = response.error;
      throw new JsonRpcError(e.code, e.message, e.data);
    } else {
      throw new JsonRpcError(-32604, 'Invalid JSON-RPC Response', response);
    }
  };

  function JsonRpcError(code, message, data) {
    this.code = code;
    this.message = message;
    this.data = data;
  }

  JsonRpcError.prototype = Object.create(Error);

  var R = window.AppRuntime;
  var t = new JsonRpcTransport(R.jsonrpc);
  var c = new JsonRpcClient(t);

  function resolveNode(root, path) {
    var segments = path.split('.');
    var parent;
    var node = root;
    var name;
    var i;
    for (i in segments) {
      name = segments[i];
      parent = node;
      if (parent[name] === undefined) {
        parent[name] = {};
      }
      node = parent[name];
    }
    if (segments.length > 0) {
      return {
        parent: parent,
        name: name,
        node: node
      };
    }
  }

  function makeProxyFn(path, name) {
    return function() {
      var args = Array.prototype.slice.call(arguments);
      // R.println('Invoking proxy ' + path + '.' + name);
      return c.invoke(path + '.' + name, args);
    };
  }

  function makeProxy(root, exported) {
    var resolved = resolveNode(root, exported.path);

    var proxy = resolved.node;
    var methods = exported.methods;
    var i;
    var name;
    R.println('Making proxy ' + exported.path);
    for (i in methods) {
      name = methods[i];
      R.println(' - ' + name);
      proxy[name] = makeProxyFn(exported.path, name);
    }
  }

  (function() {
    var exports = c.invoke('__exports__', []);
    var i;
    for (i in exports) {
      makeProxy(window, exports[i]);
    }
  })();
  R.println('------ runtime.js ends ---------------');

  return c;
}
