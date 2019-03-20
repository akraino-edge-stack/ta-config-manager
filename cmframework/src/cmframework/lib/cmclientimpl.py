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
import json
import time
import requests

from cmframework.apis import cmerror
from cmframework.apis import cmchangestate


class CMClientImpl(object):
    def __init__(self, server_ip, server_port, verbose_logger):
        self.version = 'v1.0'
        self.server_ip = server_ip
        self.server_port = server_port
        base_url = str.format('http://{ip}:{port}/cm/{api}', ip=self.server_ip,
                              port=self.server_port, api=self.version)
        self.props_base_url = str.format('{base}/properties', base=base_url)
        self.snapshots_base_url = str.format('{base}/snapshots', base=base_url)
        self.activator_url = str.format('{base}/activator', base=base_url)
        self.reboot_url = str.format('{base}/reboot', base=base_url)
        self.changes_url = str.format('{base}/changes', base=base_url)
        self.verbose_logger = verbose_logger

    def get_property(self, prop_name, snapshot_name=None):
        resource = str.format('{base}/{prop}', base=self.props_base_url, prop=prop_name)
        if snapshot_name:
            resource = str.format('{}?snapshot={snapshot}', resource, snapshot=snapshot_name)
        result = self._get_rpc(resource)
        try:
            value = result['value']
        except KeyError:
            raise cmerror.CMError('Invalid response')
        except TypeError:
            raise cmerror.CMError('Invalid response')
        except Exception as exp:  # pylint: disable=broad-except
            raise cmerror.CMError(str(exp))
        return value

    def get_properties(self, prop_filter, snapshot_name=None):
        resource = str.format('{base}?prop-name-filter={f}', base=self.props_base_url,
                              f=prop_filter)
        if snapshot_name:
            resource = str.format('{}&snapshot={snapshot}', resource,
                                  snapshot=snapshot_name)
        result = self._get_rpc(resource)
        props = {}
        try:
            properties = result['properties']
            for item in properties:
                name = item['name']
                value = item['value']
                props[name] = value
        except KeyError as exp:
            raise cmerror.CMError('Invalid response')
        except TypeError as exp:
            raise cmerror.CMError('Invalid response')
        except Exception as exp:
            raise cmerror.CMError(str(exp))
        return props

    def set_property(self, prop_name, prop_value):
        resource = str.format('{base}/{prop}', base=self.props_base_url, prop=prop_name)
        body = {}
        body['value'] = prop_value
        result = self._post_rpc(resource, body)
        return result['change-uuid']

    def set_properties(self, props, overwrite=False):
        body = {}
        items = []
        for key, value in props.iteritems():
            item = {}
            item['name'] = key
            item['value'] = value
            items.append(item)
        body['overwrite'] = overwrite
        body['properties'] = items
        result = self._post_rpc(self.props_base_url, body)
        return result['change-uuid']

    def delete_property(self, prop_name):
        resource = str.format('{base}/{prop}', base=self.props_base_url, prop=prop_name)
        result = self._delete_rpc(resource, None)
        return result['change-uuid']

    def delete_properties(self, arg):
        result = {}
        if isinstance(arg, str):
            resource = str.format('{base}?prop-name-filter={f}', base=self.props_base_url, f=arg)
            result = self._delete_rpc(resource, None)
        else:
            resource = str.format('{base}', base=self.props_base_url)
            body = {}
            body['properties'] = arg
            result = self._delete_rpc(resource, body)
        return result['change-uuid']

    def create_snapshot(self, snapshot_name):
        resource = str.format('{base}/{snapshot}',
                              base=self.snapshots_base_url,
                              snapshot=snapshot_name)
        self._get_rpc(resource)

    def restore_snapshot(self, snapshot_name):
        resource = str.format('{base}/{snapshot}',
                              base=self.snapshots_base_url,
                              snapshot=snapshot_name)
        self._post_rpc(resource, None)

    def delete_snapshot(self, snapshot_name):
        resource = str.format('{base}/{snapshot}',
                              base=self.snapshots_base_url,
                              snapshot=snapshot_name)
        self._delete_rpc(resource, None)

    def list_snapshots(self):
        resource = str.format('{base}', base=self.snapshots_base_url)
        result = self._get_rpc(resource)

        return result['snapshots']

    def activate(self, node_name):
        if not node_name:
            resource = str.format('{base}', base=self.activator_url)
        else:
            resource = str.format('{base}/{node}', base=self.activator_url, node=node_name)
        result = self._post_rpc(resource, None)

        return result['change-uuid']

    def activate_node(self, node_name):
        resource = str.format('{base}/agent/{node}', base=self.activator_url, node=node_name)
        result = self._get_rpc(resource)
        try:
            return result['reboot']
        except KeyError as exp:
            raise cmerror.CMError('Invalid response')
        except TypeError as exp:
            raise cmerror.CMError('Invalid response')
        except Exception as exp:
            raise cmerror.CMError(str(exp))

    def reboot_node(self, node_name):
        resource = str.format('{base}?node-name={f}', base=self.reboot_url, f=node_name)
        result = self._get_rpc(resource)
        try:
            return result['node-name']
        except KeyError as exp:
            raise cmerror.CMError('Invalid response')
        except TypeError as exp:
            raise cmerror.CMError('Invalid response')
        except Exception as exp:
            raise cmerror.CMError(str(exp))

    def enable_automatic_activation(self):
        resource = str.format('{base}/enable', base=self.activator_url)
        self._post_rpc(resource, None)

    def disable_automatic_activation(self):
        resource = str.format('{base}/disable', base=self.activator_url)
        self._post_rpc(resource, None)

    def get_changes_states(self, change_uuid):
        if change_uuid:
            resource = str.format('{base}?change-uuid-filter={change_uuid}',
                                  base=self.changes_url,
                                  change_uuid=change_uuid)
        else:
            resource = str.format('{base}', base=self.changes_url)
        result = self._get_rpc(resource)
        return result

    def wait_activation(self, change_uuid):
        self.verbose_log('Waiting for activation (%s) to finish' % change_uuid)
        state = None
        failed_plugins = None
        while True:
            try:
                changes = self.get_changes_states(change_uuid)
                state = changes[change_uuid]['state']
                failed_plugins = changes[change_uuid]['failed-plugins']
                self.verbose_log('State of change is %s' % state)
                if state != cmchangestate.CM_CHANGE_STATE_ONGOING:
                    break
                time.sleep(5)
            except Exception as exp:  # pylint: disable=broad-except
                raise cmerror.CMError(str(exp))

        if state != cmchangestate.CM_CHANGE_STATE_OK:
            raise cmerror.CMError("Activation was unsuccessful! Failed plugins: {}"
                                  .format(failed_plugins))

    def verbose_log(self, msg):
        if self.verbose_logger:
            self.verbose_logger(msg)

    def _get_rpc(self, resource):
        self.verbose_log('Sending GET %s' % resource)
        response = requests.get(resource)
        return self._handle_response(response)

    def _post_rpc(self, resource, body):
        self.verbose_log('Sending POST %s' % resource)
        self.verbose_log('        BODY %s' % body)
        if body:
            headers = {}
            headers['Content-type'] = 'application/json'
            response = requests.post(resource, data=json.dumps(body), headers=headers)
        else:
            response = requests.post(resource)

        return self._handle_response(response)

    def _delete_rpc(self, resource, body):
        self.verbose_log('Sending DELETE %s' % resource)
        self.verbose_log('        BODY %s' % body)
        if body:
            headers = {}
            headers['Content-type'] = 'application/json'
            response = requests.delete(resource, data=json.dumps(body), headers=headers)
        else:
            headers = {}
            headers['Content-type'] = 'text'
            response = requests.delete(resource)
        return self._handle_response(response)

    def _handle_response(self, response):
        self.verbose_log('Got STATUS %s' % response.reason)
        self.verbose_log('    CONTENT %s' % response.content)
        if not response.ok:
            raise cmerror.CMError(response.reason)

        try:
            if response.content:
                return response.json()
        except ValueError as exp:
            raise cmerror.CMError(str(exp))
        return None
