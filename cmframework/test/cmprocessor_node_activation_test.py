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

from cmframework.server.cmprocessor import CMProcessor
from cmframework.apis.cmerror import CMError
from cmframework.server.cmcsn import CMCSN

# TODO:Add the checking for calling the changemonitorhandle


class CMProcessorNodeActivationTest(unittest.TestCase):
    @staticmethod
    def backend_get_property(key):
        if key == 'cloud.cmframework':
            return '{"csn": {"global": 101, "nodes": {"node-a": 99, "node-b": 100, "node-c": 101}}}'
        elif key == 'foo':
            return '{"foo": "bar"}'

    @mock.patch('cmframework.server.cmprocessor.logging')
    @mock.patch('cmframework.server.cmprocessor.cmactivationwork.CMActivationWork')
    def test_get_property(self, mock_work, mock_logging):
        mock_backend = mock.MagicMock()
        mock_backend.get_property = CMProcessorNodeActivationTest.backend_get_property

        mock_validator = mock.MagicMock()
        mock_activator = mock.MagicMock()
        mock_changemonitor = mock.MagicMock()
        mock_activationstate_handler = mock.MagicMock()
        mock_snapshot_handler = mock.MagicMock()

        mock_work.OPER_SET = mock.MagicMock()

        processor = CMProcessor(mock_backend, mock_validator, mock_activator,
                                mock_changemonitor, mock_activationstate_handler,
                                mock_snapshot_handler)

        self.assertEqual(json.loads(processor.get_property('foo'))['foo'], 'bar')

    @mock.patch('cmframework.server.cmprocessor.logging')
    @mock.patch('cmframework.server.cmprocessor.cmactivationwork.CMActivationWork')
    def test_set_property(self, mock_work, mock_logging):
        mock_backend = mock.MagicMock()
        mock_backend.get_property = CMProcessorNodeActivationTest.backend_get_property

        mock_validator = mock.MagicMock()
        mock_activator = mock.MagicMock()
        mock_changemonitor = mock.MagicMock()
        mock_activationstate_handler = mock.MagicMock()
        mock_snapshot_handler = mock.MagicMock()

        mock_work.OPER_SET = mock.MagicMock()

        processor = CMProcessor(mock_backend, mock_validator, mock_activator,
                                mock_changemonitor, mock_activationstate_handler,
                                mock_snapshot_handler)

        processor.set_property('foo', 'barbar')

        mock_validator.validate_set.assert_called_once_with({'foo': 'barbar'})
        mock_backend.set_properties.called_once_with({'foo': 'barbar'})
        mock_work.assert_called_once_with(mock_work.OPER_SET, 102, {'foo': 'barbar'})
        mock_activator.add_work.assert_called_once_with(mock_work.return_value)

    @mock.patch('cmframework.server.cmprocessor.logging')
    @mock.patch('cmframework.server.cmprocessor.cmactivationwork.CMActivationWork')
    @mock.patch('cmframework.server.cmprocessor.cmalarm.CMActivationFailedAlarm')
    def test_activate_node_no_change(self, mock_alarm, mock_work, mock_logging):
        mock_backend = mock.MagicMock()
        mock_backend.get_property = CMProcessorNodeActivationTest.backend_get_property

        mock_validator = mock.MagicMock()
        mock_activator = mock.MagicMock()
        mock_changemonitor = mock.MagicMock()
        mock_activationstate_handler = mock.MagicMock()
        mock_snapshot_handler = mock.MagicMock()

        mock_work.return_value.get_result = mock.MagicMock()
        mock_work.return_value.get_result.return_value = None

        mock_work.OPER_NODE = mock.MagicMock()

        processor = CMProcessor(mock_backend, mock_validator, mock_activator,
                                mock_changemonitor, mock_activationstate_handler,
                                mock_snapshot_handler)

        self.assertEqual(processor.activate_node('node-c'), False)

        mock_alarm.assert_not_called()
        mock_activator.add_work.assert_not_called()

    @mock.patch('cmframework.server.cmprocessor.logging')
    @mock.patch('cmframework.server.cmprocessor.cmactivationwork.CMActivationWork')
    @mock.patch('cmframework.server.cmprocessor.cmalarm.CMActivationFailedAlarm')
    @mock.patch.object(CMProcessor, '_clear_reboot_requests')
    @mock.patch.object(CMCSN, 'sync_node_csn')
    def test_activate_node_changed_no_reboot(self, mock_sync_node_csn, mock_clear_reboot_requests,
                                             mock_alarm, mock_work, mock_logging):
        mock_backend = mock.MagicMock()
        mock_backend.get_property = CMProcessorNodeActivationTest.backend_get_property

        mock_validator = mock.MagicMock()
        mock_activator = mock.MagicMock()
        mock_changemonitor = mock.MagicMock()
        mock_activationstate_handler = mock.MagicMock()
        mock_snapshot_handler = mock.MagicMock()

        mock_work.return_value.get_result = mock.MagicMock()
        mock_work.return_value.get_result.return_value = None

        mock_work.OPER_NODE = mock.MagicMock()

        processor = CMProcessor(mock_backend, mock_validator, mock_activator,
                                mock_changemonitor, mock_activationstate_handler,
                                mock_snapshot_handler)

        self.assertEqual(processor.activate_node('node-b'), False)

        mock_clear_reboot_requests.assert_called_once()
        mock_work.assert_called_once_with(mock_work.OPER_NODE, 101, {}, 'node-b')
        mock_activator.add_work.assert_called_once_with(mock_work.return_value)
        mock_alarm.return_value.cancel_alarm_for_node.assert_called_once_with('node-b')
        mock_work.return_value.get_result.assert_called_once()
        mock_sync_node_csn.assert_called_once()
        mock_alarm.return_value.raise_alarm_for_node.assert_not_called()

    @mock.patch('cmframework.server.cmprocessor.logging')
    @mock.patch('cmframework.server.cmprocessor.cmactivationwork.CMActivationWork')
    @mock.patch('cmframework.server.cmprocessor.cmalarm.CMActivationFailedAlarm')
    @mock.patch.object(CMProcessor, '_clear_reboot_requests')
    @mock.patch.object(CMCSN, 'sync_node_csn')
    def test_activate_node_changed_and_reboot(self, mock_sync_node_csn, mock_clear_reboot_requests,
                                              mock_alarm, mock_work, mock_logging):
        mock_backend = mock.MagicMock()
        mock_backend.get_property = CMProcessorNodeActivationTest.backend_get_property

        mock_validator = mock.MagicMock()
        mock_activator = mock.MagicMock()
        mock_changemonitor = mock.MagicMock()
        mock_activationstate_handler = mock.MagicMock()
        mock_snapshot_handler = mock.MagicMock()

        mock_work.return_value.get_result = mock.MagicMock()
        mock_work.return_value.get_result.return_value = None

        mock_work.OPER_NODE = mock.MagicMock()

        processor = CMProcessor(mock_backend, mock_validator, mock_activator,
                                mock_changemonitor, mock_activationstate_handler,
                                mock_snapshot_handler)

        processor.reboot_request('node-b')

        self.assertEqual(processor.activate_node('node-b'), True)

        mock_clear_reboot_requests.assert_called_once()
        mock_work.assert_called_once_with(mock_work.OPER_NODE, 101, {}, 'node-b')
        mock_activator.add_work.assert_called_once_with(mock_work.return_value)
        mock_alarm.return_value.cancel_alarm_for_node.assert_called_once_with('node-b')
        mock_work.return_value.get_result.assert_called_once()
        mock_sync_node_csn.assert_called_once()
        mock_alarm.return_value.raise_alarm_for_node.assert_not_called()

    @mock.patch('cmframework.server.cmprocessor.logging')
    @mock.patch('cmframework.server.cmprocessor.cmactivationwork.CMActivationWork')
    @mock.patch('cmframework.server.cmprocessor.cmalarm.CMActivationFailedAlarm')
    @mock.patch.object(CMCSN, 'sync_node_csn')
    def test_activate_node_changed_activation_fails(self, mock_sync_node_csn,
                                                    mock_alarm, mock_work, mock_logging):
        mock_backend = mock.MagicMock()
        mock_backend.get_property = CMProcessorNodeActivationTest.backend_get_property

        mock_validator = mock.MagicMock()
        mock_activator = mock.MagicMock()
        mock_changemonitor = mock.MagicMock()
        mock_activationstate_handler = mock.MagicMock()
        mock_snapshot_handler = mock.MagicMock()

        mock_work.return_value.get_result = mock.MagicMock()
        mock_work.return_value.get_result.return_value = {'test handler': ['test error']}

        mock_work.OPER_NODE = mock.MagicMock()

        processor = CMProcessor(mock_backend, mock_validator, mock_activator,
                                mock_changemonitor, mock_activationstate_handler,
                                mock_snapshot_handler)

        processor.activate_node('node-b')

        mock_work.assert_called_once_with(mock_work.OPER_NODE, 101, {}, 'node-b')
        mock_activator.add_work.assert_called_once_with(mock_work.return_value)
        mock_work.return_value.get_result.assert_called_once()
        mock_sync_node_csn.assert_not_called()
        mock_alarm.return_value.assert_has_calls(
            [call.cancel_alarm_for_node('node-b'),
             call.raise_alarm_for_node('node-b', {'failed activators': ['test error']})])

if __name__ == '__main__':
    unittest.main()
