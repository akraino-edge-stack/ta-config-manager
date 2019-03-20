# Copyright 2019 Nokia

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import logging
import urllib
import urlparse
import routes

from cmframework.server.cmhttperrors import CMHTTPErrors
from cmframework.apis import cmerror
from cmframework.server import cmhttprpc


class CMWSGIHandler(object):
    def __init__(self, rest_api_factory):
        logging.debug('CMWSGIHandler constructor called')
        self.mapper = routes.Mapper()
        self.mapper.connect(None, '/cm/apis', action='get_apis')
        self.mapper.connect(None, '/cm/{api}/properties', action='handle_properties')
        self.mapper.connect(None, '/cm/{api}/properties/{property}', action='handle_property')
        self.mapper.connect(None, '/cm/{api}/snapshots', action='handle_snapshots')
        self.mapper.connect(None, '/cm/{api}/snapshots/{snapshot}', action='handle_snapshot')
        self.mapper.connect(None, '/cm/{api}/activator/enable', action='handle_activator_enable')
        self.mapper.connect(None, '/cm/{api}/activator/disable', action='handle_activator_disable')
        self.mapper.connect(None, '/cm/{api}/activator/agent/{node}',
                            action='handle_agent_activate')
        self.mapper.connect(None, '/cm/{api}/activator/{node}', action='handle_activate')
        self.mapper.connect(None, '/cm/{api}/activator', action='handle_activate')
        self.mapper.connect(None, '/cm/{api}/reboot', action='handle_reboot')
        self.mapper.connect(None, '/cm/{api}/changes', action='handle_changes')
        self.rest_api_factory = rest_api_factory

    def __call__(self, environ, start_response):
        logging.debug('Handling request started, environ=%s', str(environ))
        # for debug, print environment
        # pprint.pprint(environ)

        # For request and resonse data
        rpc = cmhttprpc.HTTPRPC()
        rpc.rep_status = CMHTTPErrors.get_ok_status()

        # get the interesting fields
        rpc.req_method = environ['REQUEST_METHOD']
        path = environ['PATH_INFO']
        try:
            rpc.req_filter = urlparse.parse_qs(urllib.unquote(environ['QUERY_STRING']))
        except KeyError as exp:
            rpc.req_filter = {}
        content_type = environ['CONTENT_TYPE']
        try:
            content_size = environ['CONTENT_LENGTH']
        except KeyError:
            content_size = None

        try:
            # get the action to be done
            action = ''
            actions, _ = self.mapper.routematch(path)
            if actions and isinstance(actions, dict):
                action = actions.get('action', '')
                for key, value in actions.iteritems():
                    if key != 'action':
                        rpc.req_params[key] = value
            else:
                rpc.rep_status = CMHTTPErrors.get_resource_not_found_status()
                raise cmerror.CMError('The requested url is not found')

            # get the body if available
            if content_size and int(content_size):
                size = int(content_size)
                if content_type == 'application/json':
                    totalread = 0
                    while totalread < size:
                        data = environ['wsgi.input'].read()
                        totalread += len(data)
                        rpc.req_body += data
                else:
                    rpc.rep_status = CMHTTPErrors.get_unsupported_content_type_status()
                    raise cmerror.CMError('Only json content is supported')

            # check the action
            try:
                logging.info('Calling %s with rpc=%s', action, str(rpc))
                actionfunc = getattr(self, action)
                actionfunc(rpc)
            except AttributeError as attrerror:
                rpc.reply_status = CMHTTPErrors.get_resource_not_found_status()
                raise cmerror.CMError('Action %s not found, error: %s' % (action, str(attrerror)))

        except cmerror.CMError as exp:
            rpc.rep_status = CMHTTPErrors.get_internal_error_status()
            rpc.rep_status += ','
            rpc.rep_status += str(exp)
        except Exception as exp:  # pylint: disable=broad-except
            rpc.rep_status = CMHTTPErrors.get_internal_error_status()
            rpc.rep_status += ','
            rpc.rep_status += str(exp)
        finally:
            logging.info('Replying with rpc=%s', str(rpc))
            response_headers = [('Content-type', 'application/json')]
            start_response(rpc.rep_status, response_headers)
            yield rpc.rep_body

    def get_apis(self, rpc):
        logging.debug('get_apis called')
        if rpc.req_method != 'GET':
            rpc.rep_status = CMHTTPErrors.get_request_not_ok_status()
            rpc.rep_status += ', only GET operation is possible'
        else:
            self.rest_api_factory.get_apis(rpc)

    def handle_properties(self, rpc):
        logging.debug('handle_properties called')
        api = self._get_api(rpc)
        if api:
            api.handle_properties(rpc)

    def handle_property(self, rpc):
        logging.debug('handle_property called')
        api = self._get_api(rpc)
        if api:
            api.handle_property(rpc)

    def handle_snapshots(self, rpc):
        logging.debug('handle_snapshots called')
        api = self._get_api(rpc)
        if api:
            api.handle_snapshots(rpc)

    def handle_snapshot(self, rpc):
        logging.debug('handle_snapshot called')
        api = self._get_api(rpc)
        if api:
            api.handle_snapshot(rpc)

    def handle_agent_activate(self, rpc):
        logging.debug('handle_agent_activate called')
        api = self._get_api(rpc)
        if api:
            api.handle_agent_activate(rpc)

    def handle_activate(self, rpc):
        logging.debug('handle_activate called')
        api = self._get_api(rpc)
        if api:
            api.handle_activate(rpc)

    def handle_activator_disable(self, rpc):
        logging.debug('handle_activator_disable called')
        api = self._get_api(rpc)
        if api:
            api.handle_activator_disable(rpc)

    def handle_activator_enable(self, rpc):
        logging.debug('handle_activator_enable called')
        api = self._get_api(rpc)
        if api:
            api.handle_activator_enable(rpc)

    def handle_reboot(self, rpc):
        logging.debug('handle_reboot called')
        api = self._get_api(rpc)
        if api:
            api.handle_reboot(rpc)

    def handle_changes(self, rpc):
        logging.debug('handle_changes called')
        api = self._get_api(rpc)
        if api:
            api.handle_changes(rpc)

    def _get_api(self, rpc):
        logging.debug('_get_api called')
        api = None
        try:
            version = rpc.req_params['api']
            api = self.rest_api_factory.get_api(version)
            if not api:
                rpc.rep_status = CMHTTPErrors.get_resource_not_found_status()
        except KeyError:
            rpc.rep_status = CMHTTPErrors.get_request_not_ok_status()
        return api
