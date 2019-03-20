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
import json

from cmframework.server.cmprocessor import CMProcessor
from cmframework.apis.cmerror import CMError
from cmframework.server.cmcsn import CMCSN
from cmframework.server import cmchangemonitor


class CMProcessorAutomaticActivationTest(unittest.TestCase):
    @staticmethod
    def backend_get_property(key):
        if key == 'cloud.cmframework':
            return '{"csn": {"global": 101, "nodes": {"node-a": 99, "node-b": 100, "node-c": 101}}}'
        elif key == 'foo':
            return '{"foo": "bar"}'

    @mock.patch('cmframework.utils.cmflagfile.os')
    @mock.patch('cmframework.server.cmprocessor.logging')
    def test_set_property_automatic_activation_disabled(self, mock_logging, mock_flagfile_os):
        mock_backend = mock.MagicMock()
        mock_backend.get_property = CMProcessorAutomaticActivationTest.backend_get_property

        mock_validator = mock.MagicMock()
        mock_activator = mock.MagicMock()
        mock_changemonitor = mock.MagicMock()
        mock_activationstate_handler = mock.MagicMock()
        mock_snapshot_handler = mock.MagicMock()

        mock_flagfile_os.path = mock.MagicMock()
        mock_flagfile_os.path.exists = mock.MagicMock()
        mock_flagfile_os.path.exists.return_value = True

        processor = CMProcessor(mock_backend, mock_validator, mock_activator,
                                mock_changemonitor, mock_activationstate_handler,
                                mock_snapshot_handler)

        processor.set_property('foo', 'barbar')

        mock_validator.validate_set.assert_called_once_with({'foo': 'barbar'})
        mock_backend.set_properties.called_once_with({'foo': 'barbar'})
        mock_activator.add_work.assert_not_called()

    @mock.patch('cmframework.utils.cmflagfile.os')
    @mock.patch('cmframework.server.cmprocessor.logging')
    def test_delete_property_automatic_activation_disabled(self, mock_logging, mock_flagfile_os):
        mock_backend = mock.MagicMock()
        mock_backend.get_property = CMProcessorAutomaticActivationTest.backend_get_property

        mock_validator = mock.MagicMock()
        mock_activator = mock.MagicMock()
        mock_changemonitor = mock.MagicMock()
        mock_activationstate_handler = mock.MagicMock()
        mock_snapshot_handler = mock.MagicMock()

        mock_flagfile_os.path = mock.MagicMock()
        mock_flagfile_os.path.exists = mock.MagicMock()
        mock_flagfile_os.path.exists.return_value = True

        processor = CMProcessor(mock_backend, mock_validator, mock_activator,
                                mock_changemonitor, mock_activationstate_handler,
                                mock_snapshot_handler)

        processor.delete_property('foo')

        mock_validator.validate_delete.assert_called_once_with(['foo'])
        mock_backend.delete_property.assert_called_once_with('foo')
        mock_activator.add_work.assert_not_called()

    @mock.patch('cmframework.utils.cmflagfile.os')
    @mock.patch('cmframework.server.cmprocessor.logging')
    @mock.patch('cmframework.server.cmprocessor.cmactivationwork.CMActivationWork')
    @mock.patch.object(CMProcessor, '_clear_reboot_requests')
    @mock.patch.object(CMCSN, 'sync_node_csn')
    def test_activate_node_automatic_activation_disabled(self,
                                                         mock_sync_node_csn,
                                                         mock_clear_reboot_requests,
                                                         mock_work,
                                                         mock_logging,
                                                         mock_flagfile_os):
        mock_backend = mock.MagicMock()
        mock_backend.get_property = CMProcessorAutomaticActivationTest.backend_get_property

        mock_validator = mock.MagicMock()
        mock_activator = mock.MagicMock()
        mock_changemonitor = mock.MagicMock()
        mock_activationstate_handler = mock.MagicMock()
        mock_snapshot_handler = mock.MagicMock()

        mock_work.return_value.get_result = mock.MagicMock()
        mock_work.return_value.get_result.return_value = None

        mock_flagfile_os.path = mock.MagicMock()
        mock_flagfile_os.path.exists = mock.MagicMock()
        mock_flagfile_os.path.exists.return_value = True

        mock_work.OPER_NODE = mock.MagicMock()

        processor = CMProcessor(mock_backend, mock_validator, mock_activator,
                                mock_changemonitor, mock_activationstate_handler,
                                mock_snapshot_handler)

        self.assertEqual(processor.activate_node('node-b'), False)

        mock_clear_reboot_requests.assert_not_called()
        mock_work.assert_not_called()
        mock_activator.add_work.assert_not_called()
        mock_sync_node_csn.assert_not_called()

if __name__ == '__main__':
    unittest.main()
