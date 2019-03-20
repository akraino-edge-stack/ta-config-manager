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

from cmframework.apis import cmerror


class CMWSGICallbacks(object):
    # pylint: disable=no-self-use, unused-argument
    def handle_properties(self, rpc):
        logging.error('handle_properties not implemented')
        raise cmerror.CMError('Not implemented')

    def handle_property(self, rpc):
        logging.error('handle_property not implemented')
        raise cmerror.CMError('Not implemented')

    def handle_snapshots(self, rpc):
        logging.error('handle_snapshots not implemented')
        raise cmerror.CMError('Not implemented')

    def handle_snapshot(self, rpc):
        logging.error('handle_snapshot not implemented')
        raise cmerror.CMError('Not implemented')

    def handle_agent_activate(self, rpc):
        logging.error('handle_agent_activate not implemented')
        raise cmerror.CMError('Not implemented')

    def handle_activate(self, rpc):
        logging.error('handle_activate not implemented')
        raise cmerror.CMError('Not implemented')

    def handle_activator_disable(self, rpc):
        logging.error('handle_activator_disable not implemented')
        raise cmerror.CMError('Not implemented')

    def handle_activator_enable(self, rpc):
        logging.error('handle_activator_enable not implemented')
        raise cmerror.CMError('Not implemented')

    def handle_reboot(self, rpc):
        logging.error('handle_reboot not implemented')
        raise cmerror.CMError('Not implemented')

    def handle_changes(self, rpc):
        logging.error('handle_changes not implemented')
        raise cmerror.CMError('Not implemented')
