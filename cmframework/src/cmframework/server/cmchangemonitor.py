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
import uuid
import copy
from cmframework.apis import cmchangestate
from cmframework.server import cmeventletrwlock


class CMChangeMonitorState(object):
    def __init__(self):
        self.state = cmchangestate.CM_CHANGE_STATE_ONGOING
        self.failed_plugins = {}


class CMChangeMonitor(object):
    def __init__(self):
        self.changes = {}
        self.lock = cmeventletrwlock.CMEventletRWLock()

    def start_change(self):
        with self.lock.writer():
            changestate = CMChangeMonitorState()
            uuid_value = str(uuid.uuid4())
            self.changes[uuid_value] = changestate
            return uuid_value

    def change_nok(self, uuid_value, failed_plugins):
        with self.lock.writer():
            if uuid_value in self.changes:
                self.changes[uuid_value].state = cmchangestate.CM_CHANGE_STATE_NOK
                self.changes[uuid_value].failed_plugins = failed_plugins
            else:
                logging.warning('Invalid change uuid %s', uuid_value)

    def change_ok(self, uuid_value):
        with self.lock.writer():
            if uuid_value in self.changes:
                self.changes[uuid_value].state = cmchangestate.CM_CHANGE_STATE_OK
            else:
                logging.warning('Invalid change uuid %s', uuid_value)

    def get_change_state(self, uuid_value):
        with self.lock.reader():
            return self.changes[uuid_value]

    def get_all_changes_states(self):
        with self.lock.reader():
            return copy.deepcopy(self.changes)
