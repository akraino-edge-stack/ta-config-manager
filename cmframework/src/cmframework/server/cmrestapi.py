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

from cmframework.server import cmwsgicallbacks
from cmframework.apis import cmerror
from cmframework.server.cmhttperrors import CMHTTPErrors


class CMRestAPI(cmwsgicallbacks.CMWSGICallbacks):
    def __init__(self, version, status, minimum_version, processor):
        logging.debug('CMRestAPI constructor called with '
                      '{version, status, min_version}{%s, %s, %s}',
                      version, status, minimum_version)
        self.version = version
        self.status = status
        self.minimum_version = minimum_version
        self.processor = processor

    def handle_property(self, rpc):
        logging.debug('handle_property called')
        if rpc.req_method == 'GET':
            self.get_property(rpc)
        elif rpc.req_method == 'POST':
            self.set_property(rpc)
        elif rpc.req_method == 'DELETE':
            self.delete_property(rpc)
        else:
            rpc.rep_status = CMHTTPErrors.get_request_not_ok_status()
            rpc.rep_status += ', only GET/POST/DELETE are possible to this resource'

    def handle_properties(self, rpc):
        logging.debug('handle_properties called')
        if rpc.req_method == 'GET':
            self.get_properties(rpc)
        elif rpc.req_method == 'POST':
            self.set_properties(rpc)
        elif rpc.req_method == 'DELETE':
            self.delete_properties(rpc)
        else:
            rpc.rep_status = CMHTTPErrors.get_request_not_ok_status()
            rpc.rep_status += ', only GET/POST/DELETE are possible to this resource'

    def handle_snapshots(self, rpc):
        logging.debug('handle_snapshots called')
        if rpc.req_method == 'GET':
            self.list_snapshots(rpc)
        else:
            rpc.rep_status = CMHTTPErrors.get_request_not_ok_status()
            rpc.rep_status += ', only GET is possible to this resource'

    def handle_snapshot(self, rpc):
        logging.debug('handle_snapshot called')
        if rpc.req_method == 'GET':
            self.create_snapshot(rpc)
        elif rpc.req_method == 'POST':
            self.restore_snapshot(rpc)
        elif rpc.req_method == 'DELETE':
            self.delete_snapshot(rpc)
        else:
            rpc.rep_status = CMHTTPErrors.get_request_not_ok_status()
            rpc.rep_status += ', only GET/POST/DELETE are possible to this resource'

    def handle_agent_activate(self, rpc):
        logging.debug('handle_agent_activate called')
        if rpc.req_method == 'GET':
            self.activate_node(rpc)
        else:
            rpc.rep_status = CMHTTPErrors.get_request_not_ok_status()
            rpc.rep_status += ', only GET is possible to this resource'

    def handle_activate(self, rpc):
        logging.debug('handle_activate called')
        if rpc.req_method == 'POST':
            self.activate(rpc)
        else:
            rpc.rep_status = CMHTTPErrors.get_request_not_ok_status()
            rpc.rep_status += ', only POST is possible to this resource'

    def handle_activator_disable(self, rpc):
        logging.debug('handle_activator_disable called')
        if rpc.req_method == 'POST':
            self.set_automatic_activation_state(rpc, False)
        else:
            rpc.rep_status = CMHTTPErrors.get_request_not_ok_status()
            rpc.rep_status += ', only POST is possible to this resource'

    def handle_activator_enable(self, rpc):
        logging.debug('handle_activator_enable called')
        if rpc.req_method == 'POST':
            self.set_automatic_activation_state(rpc, True)
        else:
            rpc.rep_status = CMHTTPErrors.get_request_not_ok_status()
            rpc.rep_status += ', only POST is possible to this resource'

    def handle_reboot(self, rpc):
        logging.debug('handle_reboot called')
        if rpc.req_method == 'GET':
            self.reboot_node(rpc)
        else:
            rpc.rep_status = CMHTTPErrors.get_request_not_ok_status()
            rpc.rep_status += ', only GET is possible to this resource'

    def handle_changes(self, rpc):
        logging.debug('handle_changes called')
        if rpc.req_method == 'GET':
            self.get_changes_states(rpc)
        else:
            rpc.rep_status = CMHTTPErrors.get_request_not_ok_status()
            rpc.rep_status += ', only GET is possible to this resource'

    # pylint: disable=no-self-use
    def get_property(self, rpc):
        logging.error('get_property not implemented')
        rpc.rep_status = CMHTTPErrors.get_resource_not_found_status()
        raise cmerror.CMError('Not implemented')

    def get_properties(self, rpc):
        logging.error('get_properties not implemented')
        rpc.rep_status = CMHTTPErrors.get_resource_not_found_status()
        raise cmerror.CMError('Not implemented')

    def set_property(self, rpc):
        logging.error('set_property not implemented')
        rpc.rep_status = CMHTTPErrors.get_resource_not_found_status()
        raise cmerror.CMError('Not implemented')

    def set_properties(self, rpc):
        logging.error('set_properties not implemented')
        rpc.rep_status = CMHTTPErrors.get_resource_not_found_status()
        raise cmerror.CMError('Not implemented')

    def delete_property(self, rpc):
        logging.error('delete_property not implemented')
        rpc.rep_status = CMHTTPErrors.get_resource_not_found_status()
        raise cmerror.CMError('Not implemented')

    def delete_properties(self, rpc):
        logging.error('delete_properties not implemented')
        rpc.rep_status = CMHTTPErrors.get_resource_not_found_status()
        raise cmerror.CMError('Not implemented')

    def create_snapshot(self, rpc):
        logging.error('create_snapshot not implemented')
        rpc.rep_status = CMHTTPErrors.get_resource_not_found_status()
        raise cmerror.CMError('Not implemented')

    def restore_snapshot(self, rpc):
        logging.error('restore_snapshot not implemented')
        rpc.rep_status = CMHTTPErrors.get_resource_not_found_status()
        raise cmerror.CMError('Not implemented')

    def delete_snapshot(self, rpc):
        logging.error('delete_snapshot not implemented')
        rpc.rep_status = CMHTTPErrors.get_resource_not_found_status()
        raise cmerror.CMError('Not implemented')

    def list_snapshots(self, rpc):
        logging.error('list_snapshots not implemented')
        rpc.rep_status = CMHTTPErrors.get_resource_not_found_status()
        raise cmerror.CMError('Not implemented')

    def activate(self, rpc):
        logging.error('activate not implemented')
        rpc.rep_status = CMHTTPErrors.get_resource_not_found_status()
        raise cmerror.CMError('Not implemented')

    def activate_node(self, rpc):
        logging.error('activate_node not implemented')
        rpc.rep_status = CMHTTPErrors.get_resource_not_found_status()
        raise cmerror.CMError('Not implemented')

    def reboot_node(self, rpc):
        logging.error('reboot_node not implemented')
        rpc.rep_status = CMHTTPErrors.get_resource_not_found_status()
        raise cmerror.CMError('Not implemented')

    def get_changes_states(self, rpc):
        logging.error('get_changes_states not implemented')
        rpc.rep_status = CMHTTPErrors.get_resource_not_found_status()
        raise cmerror.CMError('Not implemented')

    def set_automatic_activation_state(self, rpc, state):
        logging.error('set_automatic_activation_state not implemented')
        rpc.rep_status = CMHTTPErrors.get_resource_not_found_status()
        raise cmerror.CMError('Not implemented')

    def get_version(self):
        return self.version

    def get_status(self):
        return self.status

    def get_minimum_version(self):
        return self.minimum_version
