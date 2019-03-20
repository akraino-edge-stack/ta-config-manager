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

from cmframework.utils.cmalarm import CMAlarm
from cmframework.utils.cmalarm import CMRebootRequestAlarm
from cmframework.utils.cmalarm import CMActivationFailedAlarm
from cmframework.apis.cmerror import CMError


class CMAlarmTest(unittest.TestCase):
    @mock.patch('cmframework.utils.cmalarm.logging')
    @mock.patch('cmframework.utils.cmalarm.AlarmHandler')
    def test_abstract_alarm(self, mock_alarm_handler, mock_logging):
        alarm = CMAlarm()

        with self.assertRaises(NotImplementedError) as context:
            alarm.raise_alarm_for_node('node-a')

    @mock.patch('cmframework.utils.cmalarm.logging')
    @mock.patch('cmframework.utils.cmalarm.AlarmHandler')
    def test_raise_and_fail(self, mock_alarm_handler, mock_logging):
        mock_alarm_handler.side_effect = Exception
        alarm = CMRebootRequestAlarm()
        alarm.raise_alarm_for_node('node-a')

        mock_logging.warning.assert_called_once()
        mock_alarm_handler.return_value.raise_alarm_with_dn.assert_not_called()

    @mock.patch('cmframework.utils.cmalarm.logging')
    @mock.patch('cmframework.utils.cmalarm.AlarmHandler')
    def test_cancel_and_fail(self, mock_alarm_handler, mock_logging):
        mock_alarm_handler.side_effect = Exception
        alarm = CMRebootRequestAlarm()
        alarm.cancel_alarm_for_node('node-a')

        mock_logging.warning.assert_called_once()
        mock_alarm_handler.return_value.cancel_alarm_with_dn.assert_not_called()

    @mock.patch('cmframework.utils.cmalarm.logging')
    @mock.patch('cmframework.utils.cmalarm.AlarmHandler')
    def test_raise_rebootrequestalarm_for_node(self, mock_alarm_handler, mock_logging):
        alarm = CMRebootRequestAlarm()
        alarm.raise_alarm_for_node('node-a')

        mock_alarm_handler.return_value.raise_alarm_with_dn.assert_called_once_with(
            '45001',
            'NODE-node-a',
            {})

    @mock.patch('cmframework.utils.cmalarm.logging')
    @mock.patch('cmframework.utils.cmalarm.AlarmHandler')
    def test_raise_rebootrequestalarm_for_node_with_info(self, mock_alarm_handler, mock_logging):
        alarm = CMRebootRequestAlarm()
        alarm.raise_alarm_for_node('node-a', {'some': 'additional info'})

        mock_alarm_handler.return_value.raise_alarm_with_dn.assert_called_once_with(
            '45001',
            'NODE-node-a',
            {'some': 'additional info'})

    @mock.patch('cmframework.utils.cmalarm.logging')
    @mock.patch('cmframework.utils.cmalarm.AlarmHandler')
    def test_raise_rebootrequestalarm_for_sg(self, mock_alarm_handler, mock_logging):
        alarm = CMRebootRequestAlarm()
        alarm.raise_alarm_for_sg('config-manager')

        mock_alarm_handler.return_value.raise_alarm_with_dn.assert_called_once_with(
            '45001',
            'SG-config-manager',
            {})

    @mock.patch('cmframework.utils.cmalarm.logging')
    @mock.patch('cmframework.utils.cmalarm.AlarmHandler')
    def test_cancel_rebootrequestalarm_for_node(self, mock_alarm_handler, mock_logging):
        alarm = CMRebootRequestAlarm()
        alarm.cancel_alarm_for_node('node-a')

        mock_alarm_handler.return_value.cancel_alarm_with_dn.assert_called_once_with(
            '45001',
            'NODE-node-a',
            {})

    @mock.patch('cmframework.utils.cmalarm.logging')
    @mock.patch('cmframework.utils.cmalarm.AlarmHandler')
    def test_cancel_rebootrequestalarm_for_node_with_info(self, mock_alarm_handler, mock_logging):
        alarm = CMRebootRequestAlarm()
        alarm.cancel_alarm_for_node('node-a', {'some': 'additional info'})

        mock_alarm_handler.return_value.cancel_alarm_with_dn.assert_called_once_with(
            '45001',
            'NODE-node-a',
            {'some': 'additional info'})

    @mock.patch('cmframework.utils.cmalarm.logging')
    @mock.patch('cmframework.utils.cmalarm.AlarmHandler')
    def test_cancel_rebootrequestalarm_for_sg(self, mock_alarm_handler, mock_logging):
        alarm = CMRebootRequestAlarm()
        alarm.cancel_alarm_for_sg('config-manager')

        mock_alarm_handler.return_value.cancel_alarm_with_dn.assert_called_once_with(
            '45001',
            'SG-config-manager',
            {})

    @mock.patch('cmframework.utils.cmalarm.logging')
    @mock.patch('cmframework.utils.cmalarm.AlarmHandler')
    def test_raise_activationfailed_for_node(self, mock_alarm_handler, mock_logging):
        alarm = CMActivationFailedAlarm()
        alarm.raise_alarm_for_node('node-a')

        mock_alarm_handler.return_value.raise_alarm_with_dn.assert_called_once_with(
            '45002',
            'NODE-node-a',
            {})

    @mock.patch('cmframework.utils.cmalarm.logging')
    @mock.patch('cmframework.utils.cmalarm.AlarmHandler')
    def test_raise_activationfailed_for_sg(self, mock_alarm_handler, mock_logging):
        alarm = CMActivationFailedAlarm()
        alarm.raise_alarm_for_sg('config-manager')

        mock_alarm_handler.return_value.raise_alarm_with_dn.assert_called_once_with(
            '45002',
            'SG-config-manager',
            {})

    @mock.patch('cmframework.utils.cmalarm.logging')
    @mock.patch('cmframework.utils.cmalarm.AlarmHandler')
    def test_cancel_activationfailed_for_node(self, mock_alarm_handler, mock_logging):
        alarm = CMActivationFailedAlarm()
        alarm.cancel_alarm_for_node('node-a')

        mock_alarm_handler.return_value.cancel_alarm_with_dn.assert_called_once_with(
            '45002',
            'NODE-node-a',
            {})

    @mock.patch('cmframework.utils.cmalarm.logging')
    @mock.patch('cmframework.utils.cmalarm.AlarmHandler')
    def test_cancel_activationfailed_for_sg(self, mock_alarm_handler, mock_logging):
        alarm = CMActivationFailedAlarm()
        alarm.cancel_alarm_for_sg('config-manager')

        mock_alarm_handler.return_value.cancel_alarm_with_dn.assert_called_once_with(
            '45002',
            'SG-config-manager',
            {})

if __name__ == '__main__':
    unittest.main()
