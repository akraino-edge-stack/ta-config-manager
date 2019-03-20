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
import copy
import json

from cmframework.apis import cmerror


class CMCSN(object):
    CONFIG_NAME = 'cloud.cmframework'

    def __init__(self, backend_handler):
        self.backend_handler = backend_handler
        self.config = {'csn': {'global': 0, 'nodes': {}}}
        self._get_config()
        logging.info('Current csn is %d', self.get())

    def _update_csn(self, node_name=None):
        new_config = copy.deepcopy(self.config)

        if not node_name:
            new_config['csn']['global'] += 1
            logging.info('Updating csn to %d', new_config['csn']['global'])
        else:
            new_config['csn']['nodes'][node_name] = new_config['csn']['global']
            logging.info('Updating csn for node %s to %s', node_name, new_config['csn']['global'])

        self.backend_handler.set_property(CMCSN.CONFIG_NAME, json.dumps(new_config))
        self.config = new_config

    def _get_config(self):
        try:
            self.config = json.loads(self.backend_handler.get_property(CMCSN.CONFIG_NAME))
        except cmerror.CMError as exp:
            logging.info('Context id not defined')
        except Exception as exp:  # pylint: disable=broad-except
            logging.warning('Got error: %s', exp)

    def increment(self):
        self._update_csn()

    def get(self):
        return self.config['csn']['global']

    def get_node_csn(self, node_name):
        return self.config['csn']['nodes'].get(node_name, 1)

    def sync_node_csn(self, node_name):
        self._update_csn(node_name)
