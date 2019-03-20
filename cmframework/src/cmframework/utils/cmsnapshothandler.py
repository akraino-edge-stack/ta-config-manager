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


class CMSnapshotHandler(CMStateHandler):
    SNAPSHOTS_DOMAIN = 'cm.snapshots'

    def get_data(self, snapshot_name):
        logging.debug('get_data called for: %s', snapshot_name)

        data_json = self.plugin.get(CMSnapshotHandler.SNAPSHOTS_DOMAIN, snapshot_name)

        return json.loads(data_json)

    def set_data(self, snapshot_name, data):
        logging.debug('set_properties called for: %s with: %s', snapshot_name, data)

        self.plugin.set(CMSnapshotHandler.SNAPSHOTS_DOMAIN, snapshot_name, json.dumps(data))

    def snapshot_exists(self, snapshot_name):
        logging.debug('snapshot_exists called for: %s', snapshot_name)

        return self.plugin.get(CMSnapshotHandler.SNAPSHOTS_DOMAIN, snapshot_name) is not None

    def list_snapshots(self):
        logging.debug('list_snapshots called')

        snapshots = self.plugin.get_domain(CMSnapshotHandler.SNAPSHOTS_DOMAIN)

        return snapshots.keys()

    def delete_snapshot(self, snapshot_name):
        logging.debug('delete_snapshot called for: %s', snapshot_name)

        self.plugin.delete(CMSnapshotHandler.SNAPSHOTS_DOMAIN, snapshot_name)
