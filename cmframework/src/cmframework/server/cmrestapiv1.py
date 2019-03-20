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
import json

from cmframework.apis import cmerror
from cmframework.server import cmrestapi
from cmframework.server.cmhttperrors import CMHTTPErrors


class CMRestAPIV1(cmrestapi.CMRestAPI):
    def __init__(self, processor):
        logging.debug('CMRestAPIV1 constructor called')
        cmrestapi.CMRestAPI.__init__(self, 'v1.0', 'current', '1.0', processor)

    def get_property(self, rpc):
        """
            Request: GET http://<cm-vip:port>/cm/v1.0/properties/
                             <property-name>?snapshot=<snapshot name>
            Response: {
                "name": "<name of the property>",
                "value": "<value of the property>",
            }
        """

        logging.debug('get_property called')
        try:
            snapshot_name = rpc.req_filter.get('snapshot', None)
            if isinstance(snapshot_name, list):
                snapshot_name = snapshot_name[0]
            prop_name = rpc.req_params['property']
            value = self.processor.get_property(prop_name, snapshot_name)
            reply = {}
            reply['name'] = prop_name
            reply['value'] = value
            rpc.rep_status = CMHTTPErrors.get_ok_status()
            rpc.rep_body = json.dumps(reply)
        except cmerror.CMError as exp:
            rpc.rep_status = CMHTTPErrors.get_resource_not_found_status()
            rpc.rep_status += ','
            rpc.rep_status += str(exp)
        except KeyError:
            rpc.rep_status = CMHTTPErrors.get_resource_not_found_status()
        except Exception as exp:  # pylint: disable=broad-except
            rpc.rep_status = CMHTTPErrors.get_internal_error_status()
            rpc.rep_status += ','
            rpc.rep_status += str(exp)

    def get_properties(self, rpc):
        """
            Request: GET http://<cm-vip:port>/cm/v1.0/properties?
                             prop-name-filter=<filter>&snapshot=<snapshot name>
            Response: {
                "properties": [
                    {
                        "name": "<name of the property>",
                        "value": "<value of the property>"
                    },
                    {
                        "name": "<name of the property>",
                        "value": "<value of the property>"
                    }
                    ....
                ]
            }
        """

        logging.debug('get_properties called')
        try:
            prop_name_filter = rpc.req_filter.get('prop-name-filter', '')
            if isinstance(prop_name_filter, list):
                prop_name_filter = prop_name_filter[0]
            snapshot_name = rpc.req_filter.get('snapshot', None)
            if isinstance(snapshot_name, list):
                snapshot_name = snapshot_name[0]
            result = self.processor.get_properties(prop_name_filter, snapshot_name)
            if not bool(result):
                rpc.rep_status = CMHTTPErrors.get_resource_not_found_status()
            else:
                reply = {}
                items = []
                for key, value in result.iteritems():
                    tmp = {}
                    tmp['name'] = key
                    tmp['value'] = value
                    items.append(tmp)
                reply['properties'] = items
                rpc.rep_status = CMHTTPErrors.get_ok_status()
                rpc.rep_body = json.dumps(reply)
        except cmerror.CMError as exp:
            rpc.rep_status = CMHTTPErrors.get_resource_not_found_status()
            rpc.rep_status += ','
            rpc.rep_status += str(exp)
        except Exception as exp:  # pylint: disable=broad-except
            rpc.rep_status = CMHTTPErrors.get_internal_error_status()
            rpc.rep_status += ','
            rpc.rep_status += str(exp)

    def set_property(self, rpc):
        """
            Request: POST http://<cm-vip:port>/cm/v1.0/properties/<property-name>
                {
                    "value": "<value of the property>"
                }
            Response: http status set correctly
               {
                    "change-uuid": "<uuid>"
               }
        """

        logging.debug('set_property called')
        try:
            if not rpc.req_body:
                rpc.rep_status = CMHTTPErrors.get_request_not_ok_status()
            else:
                request = json.loads(rpc.req_body)
                name = rpc.req_params['property']
                value = request['value']
                uuid_value = self.processor.set_property(name, value)
                rpc.rep_status = CMHTTPErrors.get_ok_status()
                reply = {}
                reply['change-uuid'] = uuid_value
                rpc.rep_body = json.dumps(reply)
        except cmerror.CMError as exp:
            rpc.rep_status = CMHTTPErrors.get_internal_error_status()
            rpc.rep_status += ','
            rpc.rep_status += str(exp)
        except KeyError:
            rpc.rep_status = CMHTTPErrors.get_request_not_ok_status()
        except Exception as exp:  # pylint: disable=broad-except
            rpc.rep_status = CMHTTPErrors.get_internal_error_status()
            rpc.rep_status += ','
            rpc.rep_status += str(exp)

    def set_properties(self, rpc):
        """
            Request: POST http://<cm-vip:port>/cm/v1.0/properties
                {
                    "overwrite": True|False,
                    "properties": [
                        {
                            "name": "<name of the property>",
                            "value": "<value of the property>"
                        },
                        {
                            "name": "<name of the property>",
                            "value": "<value of the property>"
                        },
                        ....
                    ]
                }
            Response:
                {
                     "change-uuid": "<uuid>"
                }
        """

        logging.debug('set_properties called')
        try:
            if not rpc.req_body:
                rpc.rep_status = CMHTTPErrors.get_request_not_ok_status()
            else:
                request = json.loads(rpc.req_body)
                overwrite = False
                if 'overwrite' in request:
                    overwrite = request['overwrite']
                items = request['properties']
                data = {}
                for entry in items:
                    name = entry['name']
                    value = entry['value']
                    data[name] = value
                uuid_value = self.processor.set_properties(data, overwrite)
                rpc.rep_status = CMHTTPErrors.get_ok_status()
                reply = {}
                reply['change-uuid'] = uuid_value
                rpc.rep_body = json.dumps(reply)
        except cmerror.CMError as exp:
            rpc.rep_status = CMHTTPErrors.get_internal_error_status()
            rpc.rep_status += ','
            rpc.rep_status += str(exp)
        except KeyError:
            rpc.rep_status = CMHTTPErrors.get_request_not_ok_status()
        except Exception as exp:  # pylint: disable=broad-except
            rpc.rep_status = CMHTTPErrors.get_internal_error_status()
            rpc.rep_status += ','
            rpc.rep_status += str(exp)

    def delete_property(self, rpc):
        """
            Request: DELETE http://<cm-vip:port>/cm/v1.0/properties/<property-name>
            Response: http response with proper status
                {
                    "change-uuid": "<uuid>"
                }
        """

        logging.debug('delete_property called')
        try:
            prop = rpc.req_params['property']
            uuid_value = self.processor.delete_property(prop)
            rpc.rep_status = CMHTTPErrors.get_ok_status()
            reply = {}
            reply['change-uuid'] = uuid_value
            rpc.rep_body = json.dumps(reply)
        except cmerror.CMError as exp:
            rpc.rep_status = CMHTTPErrors.get_internal_error_status()
            rpc.rep_status += ','
            rpc.rep_status += str(exp)
        except KeyError:
            rpc.rep_status = CMHTTPErrors.get_request_not_ok_status()
        except Exception as exp:  # pylint: disable=broad-except
            rpc.rep_status = CMHTTPErrors.get_internal_error_status()
            rpc.rep_status += ','
            rpc.rep_status += str(exp)

    def delete_properties(self, rpc):
        """
            Request: DELETE http://<cm-vip:port>/cm/v1.0/properties?prop-name-filter=<filter>
                {
                    'properties': [ <prop-name>,
                                    <prop-name>,
                                    ....
                                  ]
                }
            Response: http response with proper status
               {
                    "change-uuid": "<uuid>"
               }
        """

        logging.debug('delete_properties called')
        try:
            if not rpc.req_filter and not rpc.req_body:
                rpc.rep_status = CMHTTPErrors.get_request_not_ok_status()
            else:
                if rpc.req_filter:
                    arg = rpc.req_filter.get('prop-name-filter', '')
                    if isinstance(arg, list):
                        arg = arg[0]
                else:
                    body = json.loads(rpc.req_body)
                    arg = body['properties']
                uuid_value = self.processor.delete_properties(arg)
                rpc.rep_status = CMHTTPErrors.get_ok_status()
                reply = {}
                reply['change-uuid'] = uuid_value
                rpc.rep_body = json.dumps(reply)
        except cmerror.CMError as exp:
            rpc.rep_status = CMHTTPErrors.get_internal_error_status()
            rpc.rep_status += ','
            rpc.rep_status += str(exp)
        except KeyError:
            rpc.rep_status = CMHTTPErrors.get_request_not_ok_status()
        except Exception as exp:  # pylint: disable=broad-except
            rpc.rep_status = CMHTTPErrors.get_internal_error_status()
            rpc.rep_status += ','
            rpc.rep_status += str(exp)

    def create_snapshot(self, rpc):
        """
            Request: GET http://<cm-vip:port>/cm/v1.0/snapshots/<snapshot name>
            Response: http response with proper status
        """

        logging.debug('create snapshot called')
        try:
            snapshot_name = rpc.req_params['snapshot']
            self.processor.create_snapshot(snapshot_name)
            rpc.rep_status = CMHTTPErrors.get_ok_status()
        except cmerror.CMError as exp:
            rpc.rep_status = CMHTTPErrors.get_internal_error_status()
            rpc.rep_status += ','
            rpc.rep_status += str(exp)
        except Exception as exp:  # pylint: disable=broad-except
            rpc.rep_status = CMHTTPErrors.get_internal_error_status()
            rpc.rep_status += ','
            rpc.rep_status += str(exp)

    def restore_snapshot(self, rpc):
        """
            Request: POST http://<cm-vip:port>/cm/v1.0/snapshots/<snapshot name>
            Response: http response with proper status
        """

        logging.debug('restore_snapshot called')
        try:
            snapshot_name = rpc.req_params['snapshot']
            self.processor.restore_snapshot(snapshot_name)
            rpc.rep_status = CMHTTPErrors.get_ok_status()
        except cmerror.CMError as exp:
            rpc.rep_status = CMHTTPErrors.get_internal_error_status()
            rpc.rep_status += ','
            rpc.rep_status += str(exp)
        except Exception as exp:
            rpc.rep_status = CMHTTPErrors.get_internal_error_status()
            rpc.rep_status += ','
            rpc.rep_status += str(exp)

    def delete_snapshot(self, rpc):
        """
            Request: DELETE http://<cm-vip:port>/cm/v1.0/snapshots/<snapshot name>
            Response: http response with proper status
        """

        logging.debug('delete_snapshot called')
        try:
            snapshot_name = rpc.req_params['snapshot']
            self.processor.delete_snapshot(snapshot_name)
            rpc.rep_status = CMHTTPErrors.get_ok_status()
        except cmerror.CMError as exp:
            rpc.rep_status = CMHTTPErrors.get_internal_error_status()
            rpc.rep_status += ','
            rpc.rep_status += str(exp)
        except KeyError as exp:
            rpc.rep_status = CMHTTPErrors.get_request_not_ok_status()
        except Exception as exp:
            rpc.rep_status = CMHTTPErrors.get_internal_error_status()
            rpc.rep_status += ','
            rpc.rep_status += str(exp)

    def list_snapshots(self, rpc):
        """
            Request: GET http://<cm-vip:port>/cm/v1.0/snapshots
            Response: {
                "snapshots": [
                    "<name of the snapshot>",
                    ....
                ]
            }
        """

        logging.debug('list_snapshots called')
        try:
            snapshots = self.processor.list_snapshots()
            if not bool(snapshots):
                rpc.rep_status = CMHTTPErrors.get_resource_not_found_status()
            else:
                reply = {}
                reply['snapshots'] = snapshots
                rpc.rep_status = CMHTTPErrors.get_ok_status()
                rpc.rep_body = json.dumps(reply)
        except cmerror.CMError as exp:
            rpc.rep_status = CMHTTPErrors.get_resource_not_found_status()
            rpc.rep_status += ','
            rpc.rep_status += str(exp)
        except Exception as exp:  # pylint: disable=broad-except
            rpc.rep_status = CMHTTPErrors.get_internal_error_status()
            rpc.rep_status += ','
            rpc.rep_status += str(exp)

    def activate(self, rpc):
        """
            Request: POST http://<cm-vip:port>/cm/v1.0/activator/<node-name>
            Response: http response with proper status
            {
                "change-uuid": "<uuid>"
            }
        """

        logging.debug('activate called')
        try:
            node_name = rpc.req_params.get('node', None)
            uuid_value = self.processor.activate(node_name)
            rpc.rep_status = CMHTTPErrors.get_ok_status()
            reply = {}
            reply['change-uuid'] = uuid_value
            rpc.rep_body = json.dumps(reply)
        except cmerror.CMError as exp:
            rpc.rep_status = CMHTTPErrors.get_internal_error_status()
            rpc.rep_status += ','
            rpc.rep_status += str(exp)
        except Exception as exp:  # pylint: disable=broad-except
            rpc.rep_status = CMHTTPErrors.get_internal_error_status()
            rpc.rep_status += ','
            rpc.rep_status += str(exp)

    def activate_node(self, rpc):
        """
            Request: GET http://<cm-vip:port>/cm/v1.0/activator/agent/<node name>
            Response: {
                "name": "<name of the node>",
                "reboot": "<boolean value indicating whether a reboot is needed>",
            }
        """

        logging.debug('activate_node called')
        try:
            node_name = rpc.req_params['node']
            reboot_needed = self.processor.activate_node(node_name)
            reply = {}
            reply['name'] = node_name
            reply['reboot'] = reboot_needed
            rpc.rep_status = CMHTTPErrors.get_ok_status()
            rpc.rep_body = json.dumps(reply)
        except cmerror.CMError as exp:
            rpc.rep_status = CMHTTPErrors.get_internal_error_status()
            rpc.rep_status += ','
            rpc.rep_status += str(exp)
        except Exception as exp:  # pylint: disable=broad-except
            rpc.rep_status = CMHTTPErrors.get_internal_error_status()
            rpc.rep_status += ','
            rpc.rep_status += str(exp)

    def set_automatic_activation_state(self, rpc, state):
        """
            Request: POST http://<cm-vip:port>/cm/v1.0/activator/disable
            or       POST http://<cm-vip:port>/cm/v1.0/activator/enable
            Response: http response with proper status
        """

        logging.debug('set_automatic_activation_state called')
        try:
            self.processor.set_automatic_activation_state(state)
            rpc.rep_status = CMHTTPErrors.get_ok_status()
        except cmerror.CMError as exp:
            rpc.rep_status = CMHTTPErrors.get_internal_error_status()
            rpc.rep_status += ','
            rpc.rep_status += str(exp)
        except Exception as exp:  # pylint: disable=broad-except
            rpc.rep_status = CMHTTPErrors.get_internal_error_status()
            rpc.rep_status += ','
            rpc.rep_status += str(exp)

    def reboot_node(self, rpc):
        """
            Request: GET http://<cm-vip:port>/cm/v1.0/reboot?node-name=<node name>
            Response: {
                "node-name": "<name of the node>",
            }
        """

        logging.debug('reboot_node called')
        try:
            if not rpc.req_filter:
                rpc.rep_status = CMHTTPErrors.get_request_not_ok_status()
            else:
                node_name = rpc.req_filter.get('node-name', None)
                if isinstance(node_name, list):
                    node_name = node_name[0]
                self.processor.reboot_request(node_name)
                reply = {}
                reply['node-name'] = node_name
                rpc.rep_status = CMHTTPErrors.get_ok_status()
                rpc.rep_body = json.dumps(reply)
        except cmerror.CMError as exp:
            rpc.rep_status = CMHTTPErrors.get_internal_error_status()
            rpc.rep_status += ','
            rpc.rep_status += str(exp)
        except Exception as exp:  # pylint: disable=broad-except
            rpc.rep_status = CMHTTPErrors.get_internal_error_status()
            rpc.rep_status += ','
            rpc.rep_status += str(exp)

    def get_changes_states(self, rpc):
        """
            Request: GET http://<cm-vip:port>/cm/v1.0/changes?changd-uuid-filter=<filter>
            Response: {
                "<change-uuid>"" : {
                                    "state": "<state>",
                                    "failed-plugins": { "plugin-name":"error",  ... }
                ...
            }
        """

        logging.debug('get_changes_states called')
        try:
            reply = {}
            changemonitor = self.processor.changemonitor
            change_uuid_value = None
            change_uuid_list = rpc.req_filter.get('change-uuid-filter', None)
            if change_uuid_list:
                change_uuid_value = change_uuid_list[0]
                state = changemonitor.get_change_state(change_uuid_value)
                reply[change_uuid_value] = {}
                reply[change_uuid_value]["state"] = state.state
                reply[change_uuid_value]["failed-plugins"] = state.failed_plugins
            else:
                changes = changemonitor.get_all_changes_states()
                for change_uuid, state in changes.iteritems():
                    reply[change_uuid] = {}
                    reply[change_uuid]["state"] = state.state
                    reply[change_uuid]["failed-plugins"] = state.failed_plugins

            rpc.rep_status = CMHTTPErrors.get_ok_status()
            rpc.rep_body = json.dumps(reply)
        except cmerror.CMError as exp:
            rpc.rep_status = CMHTTPErrors.get_resource_not_found_status()
            rpc.rep_status += ','
            rpc.rep_status += str(exp)
        except KeyError:
            rpc.rep_status = CMHTTPErrors.get_resource_not_found_status()
        except Exception as exp:  # pylint: disable=broad-except
            rpc.rep_status = CMHTTPErrors.get_internal_error_status()
            rpc.rep_status += ','
            rpc.rep_status += str(exp)
