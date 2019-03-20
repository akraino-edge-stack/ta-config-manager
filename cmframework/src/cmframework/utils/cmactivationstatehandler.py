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
from __future__ import print_function
import logging
import json

from cmframework.utils.cmstatehandler import CMStateHandler


class CMActivationStateHandler(CMStateHandler):
    def set_full_failed(self, failed_activators):
        logging.debug('set_full_failed called with: %s', failed_activators)

        self.plugin.set('cm.activation_status', 'full', json.dumps(failed_activators))

    def get_full_failed(self):
        logging.debug('get_full_failed called')

        full_failed = self.plugin.get('cm.activation_status', 'full')
        if not full_failed:
            return []

        return json.loads(full_failed)

    def clear_full_failed(self):
        logging.debug('clear_full_failed called')

        self.plugin.set('cm.activation_status', 'full', json.dumps([]))
