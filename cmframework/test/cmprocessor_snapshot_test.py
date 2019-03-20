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

from cmframework.server.cmprocessor import CMProcessor
from cmframework.apis.cmerror import CMError
from cmframework.server.cmcsn import CMCSN
from cmframework.server import cmchangemonitor


class CMProcessorSnapshotTest(unittest.TestCase):
    @mock.patch('cmframework.server.cmprocessor.cmcsn.CMCSN')
    @mock.patch('cmframework.server.cmprocessor.cmsnapshot.CMSnapshot')
    @mock.patch('cmframework.server.cmprocessor.logging')
    def test_get_property(self, mock_logging, mock_cmsnapshot, mock_cmcsn):
        mock_backend = mock.MagicMock()

        mock_validator = mock.MagicMock()
        mock_activator = mock.MagicMock()
        mock_changemonitor = mock.MagicMock()
        mock_activationstate_handler = mock.MagicMock()
        mock_snapshot_handler = mock.MagicMock()

        processor = CMProcessor(mock_backend, mock_validator, mock_activator,
                                mock_changemonitor, mock_activationstate_handler,
                                mock_snapshot_handler)

        property = processor.get_property('foo')
        mock_cmsnapshot.return_value.assert_not_called()

        snapshot_property = processor.get_property('foo', 'snap1')
        mock_cmsnapshot.return_value.assert_has_calls([call.load('snap1'),
                                                       call.get_property('foo')],
                                                      any_order=True)

    @mock.patch('cmframework.server.cmprocessor.cmcsn.CMCSN')
    @mock.patch('cmframework.server.cmprocessor.cmsnapshot.CMSnapshot')
    @mock.patch('cmframework.server.cmprocessor.logging')
    def test_get_properties(self, mock_logging, mock_cmsnapshot, mock_cmcsn):
        mock_backend = mock.MagicMock()

        mock_validator = mock.MagicMock()
        mock_activator = mock.MagicMock()
        mock_changemonitor = mock.MagicMock()
        mock_activationstate_handler = mock.MagicMock()
        mock_snapshot_handler = mock.MagicMock()

        processor = CMProcessor(mock_backend, mock_validator, mock_activator,
                                mock_changemonitor, mock_activationstate_handler,
                                mock_snapshot_handler)

        property = processor.get_properties('.*')
        mock_cmsnapshot.return_value.assert_not_called()

        snapshot_property = processor.get_properties('.*', 'snap1')
        mock_cmsnapshot.return_value.assert_has_calls([call.load('snap1'),
                                                       call.get_properties('.*')],
                                                      any_order=True)

    @mock.patch('cmframework.server.cmprocessor.cmcsn.CMCSN')
    @mock.patch('cmframework.server.cmprocessor.cmsnapshot.CMSnapshot')
    @mock.patch('cmframework.server.cmprocessor.logging')
    def test_create_snapshot(self, mock_logging, mock_cmsnapshot, mock_cmcsn):
        mock_backend = mock.MagicMock()

        mock_validator = mock.MagicMock()
        mock_activator = mock.MagicMock()
        mock_changemonitor = mock.MagicMock()
        mock_activationstate_handler = mock.MagicMock()
        mock_snapshot_handler = mock.MagicMock()

        processor = CMProcessor(mock_backend, mock_validator, mock_activator,
                                mock_changemonitor, mock_activationstate_handler,
                                mock_snapshot_handler)

        processor.create_snapshot('snap1')

        mock_cmsnapshot.return_value.create.assert_called_once_with('snap1', mock_backend)

    @mock.patch('cmframework.server.cmprocessor.cmcsn.CMCSN')
    @mock.patch('cmframework.server.cmprocessor.cmsnapshot.CMSnapshot')
    @mock.patch('cmframework.server.cmprocessor.logging')
    def test_delete_snapshot(self, mock_logging, mock_cmsnapshot, mock_cmcsn):
        mock_backend = mock.MagicMock()

        mock_validator = mock.MagicMock()
        mock_activator = mock.MagicMock()
        mock_changemonitor = mock.MagicMock()
        mock_activationstate_handler = mock.MagicMock()
        mock_snapshot_handler = mock.MagicMock()

        processor = CMProcessor(mock_backend, mock_validator, mock_activator,
                                mock_changemonitor, mock_activationstate_handler,
                                mock_snapshot_handler)

        processor.delete_snapshot('snap1')

        mock_cmsnapshot.return_value.delete.assert_called_once_with('snap1')

    @mock.patch('cmframework.server.cmprocessor.cmcsn.CMCSN')
    @mock.patch('cmframework.server.cmprocessor.cmsnapshot.CMSnapshot')
    @mock.patch('cmframework.server.cmprocessor.logging')
    def test_list_snapshots(self, mock_logging, mock_cmsnapshot, mock_cmcsn):
        mock_backend = mock.MagicMock()

        mock_validator = mock.MagicMock()
        mock_activator = mock.MagicMock()
        mock_changemonitor = mock.MagicMock()
        mock_activationstate_handler = mock.MagicMock()
        mock_snapshot_handler = mock.MagicMock()

        processor = CMProcessor(mock_backend, mock_validator, mock_activator,
                                mock_changemonitor, mock_activationstate_handler,
                                mock_snapshot_handler)

        processor.list_snapshots()

        mock_cmsnapshot.return_value.list.assert_called_once()

    @mock.patch('cmframework.server.cmprocessor.cmactivationwork.CMActivationWork')
    @mock.patch('cmframework.server.cmprocessor.cmcsn.CMCSN')
    @mock.patch('cmframework.server.cmprocessor.cmsnapshot.CMSnapshot')
    @mock.patch('cmframework.server.cmprocessor.logging')
    def test_restore_snapshot(self,
                              mock_logging,
                              mock_cmsnapshot,
                              mock_cmcsn,
                              mock_cmactivationwork):
        csn1 = mock.MagicMock()
        csn2 = mock.MagicMock()
        mock_cmcsn.side_effect = [csn1, csn2]
        mock_backend = mock.MagicMock()

        mock_validator = mock.MagicMock()
        mock_activator = mock.MagicMock()
        mock_changemonitor = mock.MagicMock()
        mock_activationstate_handler = mock.MagicMock()
        mock_snapshot_handler = mock.MagicMock()

        processor = CMProcessor(mock_backend, mock_validator, mock_activator,
                                mock_changemonitor, mock_activationstate_handler,
                                mock_snapshot_handler)

        self.assertEqual(processor.csn, csn1)

        processor.restore_snapshot('snap1')

        self.assertEqual(processor.csn, csn2)
        mock_cmsnapshot.return_value.load.assert_called_once_with('snap1')
        mock_validator.validate_set.assert_called_once_with(
            mock_cmsnapshot.return_value.get_properties.return_value)
        mock_cmsnapshot.return_value.restore.assert_called_once_with(mock_backend)
        mock_cmactivationwork.assert_called_once_with(
            mock_cmactivationwork.OPER_SET,
            csn2.get.return_value,
            mock_cmsnapshot.return_value.get_properties.return_value)
        mock_activator.add_work.assert_called_once_with(mock_cmactivationwork.return_value)

if __name__ == '__main__':
    unittest.main()
