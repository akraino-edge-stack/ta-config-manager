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

import unittest
import mock
from mock import call
import json

from cmframework.server.cmsnapshot import CMSnapshot
from cmframework.apis.cmerror import CMError


class CMSnapshotTest(unittest.TestCase):
    @staticmethod
    def snapshot_list_data(name):
        return {'snapshot_properties': {'some': 'value'},
                'snapshot_metadata': 'meta-{}'.format(name)}

    @mock.patch('cmframework.server.cmsnapshot.logging')
    def test_new_snapshot_object(self, mock_logging):
        mock_handler = mock.MagicMock()

        snapshot = CMSnapshot(mock_handler)

        with self.assertRaises(CMError) as context:
            snapshot.get_property('foo')

    @mock.patch('cmframework.server.cmsnapshot.logging')
    def test_restore_without_load(self, mock_logging):
        mock_handler = mock.MagicMock()

        mock_target_backend = mock.MagicMock()
        mock_target_backend.get_properties.return_value = {"foo": "bar",
                                                           "some": {"other": "value"}}

        snapshot = CMSnapshot(mock_handler)

        with self.assertRaises(CMError) as context:
            snapshot.restore(mock_target_backend)

    @mock.patch('cmframework.server.cmsnapshot.datetime.datetime')
    @mock.patch('cmframework.server.cmsnapshot.logging')
    def test_create(self, mock_logging, mock_datetime):
        mock_handler = mock.MagicMock()
        mock_handler.snapshot_exists.return_value = False

        mock_source_backend = mock.MagicMock()
        mock_source_backend.get_properties.return_value = {"foo": "bar", "some": {"other": "value"}}
        mock_source_backend.get_property.return_value = 'some'

        mock_datetime.now = mock.MagicMock()
        from datetime import datetime
        mock_datetime.now.return_value = datetime.now()
        expected_creation_date = mock_datetime.now.return_value.isoformat()

        snapshot = CMSnapshot(mock_handler)
        snapshot.create('snap1', mock_source_backend)

        mock_handler.set_data.assert_called_once_with(
            'snap1',
            {'snapshot_properties': mock_source_backend.get_properties.return_value,
             'snapshot_metadata': {'name': 'snap1',
                                   'creation_date': expected_creation_date,
                                   'custom': None}})

    @mock.patch('cmframework.server.cmsnapshot.logging')
    def test_create_already_exists(self, mock_logging):
        mock_handler = mock.MagicMock()
        mock_handler.snapshot_exists.return_value = True

        mock_backend_handler = mock.MagicMock()

        snapshot = CMSnapshot(mock_handler)

        with self.assertRaises(CMError) as context:
            snapshot.create('already_exists', mock_backend_handler)

    @mock.patch('cmframework.server.cmsnapshot.logging')
    def test_load_non_existing(self, mock_logging):
        mock_handler = mock.MagicMock()
        mock_handler.snapshot_exists.return_value = False

        snapshot = CMSnapshot(mock_handler)

        with self.assertRaises(CMError) as context:
            snapshot.load('snap1')

    @mock.patch('cmframework.server.cmsnapshot.logging')
    def test_load(self, mock_logging):
        expected_data = {'some': 'value'}
        expected_metadata = {'name': 'snap1',
                             'creation_date': 'somedate',
                             'custom': None}

        mock_handler = mock.MagicMock()
        mock_handler.snapshot_exists.return_value = True
        mock_handler.get_data.return_value = {
            'snapshot_properties': expected_data,
            'snapshot_metadata': expected_metadata}

        snapshot = CMSnapshot(mock_handler)

        snapshot.load('already_exists')

        assert snapshot._data == expected_data
        assert snapshot._metadata == expected_metadata

    @mock.patch('cmframework.server.cmsnapshot.logging')
    def test_restore(self, mock_logging):
        expected_data = {'foo': 'bar', 'some': {'other': 'value'}}
        expected_metadata = {'name': 'already_exists',
                             'creation_date': 'somedate',
                             'custom': None}

        mock_handler = mock.MagicMock()
        mock_handler.snapshot_exists.return_value = True
        mock_handler.get_data.return_value = {
            'snapshot_properties': expected_data,
            'snapshot_metadata': expected_metadata}

        target_backend = mock.MagicMock()
        target_backend.get_properties.return_value = {"a": "1", "b": "2"}

        snapshot = CMSnapshot(mock_handler)
        snapshot.load('already_exists')

        snapshot.restore(target_backend)

        assert {'a', 'b'} == set(target_backend.delete_properties.call_args[0][0])
        target_backend.set_properties.assert_called_once_with(expected_data)

    @mock.patch('cmframework.server.cmsnapshot.logging')
    def test_restore_only_one_in_target(self, mock_logging):
        expected_data = {'foo': 'bar', 'some': {'other': 'value'}}
        expected_metadata = {'name': 'already_exists',
                             'creation_date': 'somedate',
                             'custom': None}

        mock_handler = mock.MagicMock()
        mock_handler.snapshot_exists.return_value = True
        mock_handler.get_data.return_value = {
            'snapshot_properties': expected_data,
            'snapshot_metadata': expected_metadata}

        target_backend = mock.MagicMock()
        target_backend.get_properties.return_value = {"a": "1"}

        snapshot = CMSnapshot(mock_handler)
        snapshot.load('already_exists')

        snapshot.restore(target_backend)

        target_backend.delete_property.assert_called_once_with('a')
        target_backend.set_properties.assert_called_once_with(expected_data)

    @mock.patch('cmframework.server.cmsnapshot.logging')
    def test_list(self, mock_logging):
        mock_handler = mock.MagicMock()
        mock_handler.get_data.side_effect = CMSnapshotTest.snapshot_list_data
        mock_handler.list_snapshots.return_value = {'snap1', 'snap2'}

        expected_snapshot_list = {'meta-snap1', 'meta-snap2'}

        snapshot = CMSnapshot(mock_handler)
        snapshot_list = snapshot.list()

        assert set(snapshot_list) == expected_snapshot_list

    @mock.patch('cmframework.server.cmsnapshot.logging')
    def test_delete(self, mock_logging):
        mock_handler = mock.MagicMock()
        mock_handler.snapshot_exists.return_value = True

        snapshot = CMSnapshot(mock_handler)
        snapshot.delete('already_exists')

        mock_handler.delete_snapshot.assert_called_once_with('already_exists')

    @mock.patch('cmframework.server.cmsnapshot.logging')
    def test_delete_non_existing(self, mock_logging):
        mock_handler = mock.MagicMock()
        mock_handler.snapshot_exists.return_value = False

        snapshot = CMSnapshot(mock_handler)

        with self.assertRaises(CMError) as context:
            snapshot.delete('snap1')

if __name__ == '__main__':
    unittest.main()
