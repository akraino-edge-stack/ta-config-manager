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
import re
import datetime

from cmframework.apis import cmerror


class CMSnapshot(object):
    def __init__(self, handler):
        logging.debug('CMSnapshot constructed')

        self._handler = handler
        self._metadata = {}
        self._data = {}

    def get_property(self, prop_name):
        if not self._metadata:
            raise cmerror.CMError('No data: create or load first')

        properties = self.get_properties(prop_name)

        return properties.get(prop_name)

    def get_properties(self, prop_filter='.*'):
        if not self._data:
            raise cmerror.CMError('No data: create or load first')

        matched_properties = {}
        pattern = re.compile(prop_filter)
        for key, value in self._data:
            if pattern.match(key):
                matched_properties[key] = value

        return matched_properties

    def create(self, snapshot_name, source_backend, custom_metadata=None):
        logging.debug('create_snapshot called, snapshot name is %s', snapshot_name)

        if self._handler.snapshot_exists(snapshot_name):
            raise cmerror.CMError('Snapshot already exist')

        self._metadata = {}
        self._metadata['name'] = snapshot_name
        self._metadata['creation_date'] = datetime.datetime.now().isoformat()
        self._metadata['custom'] = custom_metadata

        self._data = source_backend.get_properties('.*')

        snapshot_data = {'snapshot_properties': self._data, 'snapshot_metadata': self._metadata}
        self._handler.set_data(snapshot_name, snapshot_data)

    def load(self, snapshot_name):
        logging.debug('load_snapshot called, snapshot name is %s', snapshot_name)

        if not self._handler.snapshot_exists(snapshot_name):
            raise cmerror.CMError('Snapshot does not exist')

        snapshot_data = self._handler.get_data(snapshot_name)

        self._metadata = snapshot_data.get('snapshot_metadata')
        if not self._metadata:
            raise cmerror.CMError('Could not load snapshot metadata for {}'.format(snapshot_name))

        self._data = snapshot_data.get('snapshot_properties')

    def restore(self, target_backend):
        logging.debug('restore_snapshot called')

        if not self._data:
            raise cmerror.CMError('No data: create or load first')

        current_properties = target_backend.get_properties('.*')
        current_keys = current_properties.keys()

        if len(current_keys) == 1:
            target_backend.delete_property(current_keys[0])
        else:
            target_backend.delete_properties(current_keys)

        target_backend.set_properties(self._data)

    def list(self):
        logging.debug('list_snapshots called')

        snapshots = []

        snapshot_names = self._handler.list_snapshots()

        for snapshot_name in snapshot_names:
            snapshot_data = self._handler.get_data(snapshot_name)
            metadata = snapshot_data.get('snapshot_metadata')
            if not metadata:
                logging.warning('Could not load snapshot metadata for %s', snapshot_name)
                continue

            snapshots.append(metadata)

        return snapshots

    def delete(self, snapshot_name):
        logging.debug('delete_snapshot called, snapshot name is %s', snapshot_name)

        if not self._handler.snapshot_exists(snapshot_name):
            raise cmerror.CMError('Snapshot does not exist')

        self._handler.delete_snapshot(snapshot_name)
