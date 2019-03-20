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
from cmframework.agent.cmagent import CMAgent
from cmframework.apis.cmerror import CMError


class CMAgentTest(unittest.TestCase):
    @mock.patch('cmframework.agent.cmagent.cmmanage.CMManage')
    @mock.patch('cmframework.agent.cmagent.cmlogger.CMLogger')
    @mock.patch('cmframework.agent.cmagent.socket.gethostbyname')
    @mock.patch('cmframework.agent.cmagent.CMAgent._reboot_node')
    @mock.patch('cmframework.agent.cmagent.VerboseLogger')
    @mock.patch('cmframework.agent.cmagent.logging')
    def test_activate_default_args_and_reboot(self, mock_logging, mock_verboselogger,
                                              mock_reboot_node, mock_socket_get_hostbyname,
                                              mock_cmlogger, mock_cmmanage):
        mock_cmmanage.return_value.activate_node = mock.MagicMock(return_value=True)
        mock_reboot_node.return_value = 0
        args = []
        agent = CMAgent()
        agent(args)

        # import pdb
        # pdb.set_trace()

        mock_socket_get_hostbyname.assert_called_once_with('config-manager')

        mock_cmmanage.assert_called_once_with(mock_socket_get_hostbyname.return_value, 61100,
                                              'cmframework.lib.CMClientImpl',
                                              mock_verboselogger.return_value)
        mock_cmmanage.return_value.activate_node.assert_called_once()
        mock_reboot_node.assert_called_once()

    @mock.patch('cmframework.agent.cmagent.cmmanage.CMManage')
    @mock.patch('cmframework.agent.cmagent.cmlogger.CMLogger')
    @mock.patch('cmframework.agent.cmagent.socket.gethostbyname')
    @mock.patch('cmframework.agent.cmagent.CMAgent._reboot_node')
    @mock.patch('cmframework.agent.cmagent.VerboseLogger')
    @mock.patch('cmframework.agent.cmagent.logging')
    def test_activate_no_reboot(self, mock_logging, mock_verboselogger, mock_reboot_node,
                                mock_socket_get_hostbyname, mock_cmlogger, mock_cmmanage):
        mock_cmmanage.return_value.activate_node = mock.MagicMock(return_value=False)
        args = []
        agent = CMAgent()
        agent(args)

        mock_cmmanage.return_value.activate_node.assert_called_once()
        mock_reboot_node.assert_not_called()

    @mock.patch('cmframework.agent.cmagent.cmmanage.CMManage')
    @mock.patch('cmframework.agent.cmagent.cmlogger.CMLogger')
    @mock.patch('cmframework.agent.cmagent.socket.gethostbyname')
    @mock.patch('cmframework.agent.cmagent.CMAgent._reboot_node')
    @mock.patch('cmframework.agent.cmagent.VerboseLogger')
    @mock.patch('cmframework.agent.cmagent.logging')
    def test_activate_custom_args(self, mock_logging, mock_verboselogger, mock_reboot_node,
                                  mock_socket_get_hostbyname, mock_cmlogger, mock_cmmanage):
        mock_cmmanage.return_value.activate_node = mock.MagicMock(return_value=True)

        args = ['--ip', 'abc.com', '--port', '1234', '--client-lib', 'abc']
        agent = CMAgent()
        agent(args)

        mock_socket_get_hostbyname.assert_called_once_with('abc.com')

        mock_cmmanage.assert_called_once_with(mock_socket_get_hostbyname.return_value, 1234, 'abc',
                                              mock_verboselogger.return_value)
        mock_cmmanage.return_value.activate_node.assert_called_once()

    @mock.patch('cmframework.agent.cmagent.cmmanage.CMManage')
    @mock.patch('cmframework.agent.cmagent.cmlogger.CMLogger')
    @mock.patch('cmframework.agent.cmagent.socket.gethostbyname')
    @mock.patch('cmframework.agent.cmagent.CMAgent._reboot_node')
    @mock.patch('cmframework.agent.cmagent.VerboseLogger')
    @mock.patch('cmframework.agent.cmagent.logging')
    def test_activate_localhost(self, mock_logging, mock_verboselogger, mock_reboot_node,
                                mock_socket_get_hostbyname, mock_cmlogger, mock_cmmanage):
        mock_cmmanage.return_value.activate_node = mock.MagicMock(return_value=True)

        import socket
        mock_socket_get_hostbyname.side_effect = socket.gaierror()

        args = []
        agent = CMAgent()
        agent(args)

        mock_socket_get_hostbyname.assert_called_once_with('config-manager')
        mock_verboselogger.assert_called_once()

        mock_cmmanage.assert_called_once_with('127.0.0.1', 61100,
                                              'cmframework.lib.CMClientImpl',
                                              mock_verboselogger.return_value)
        mock_cmmanage.return_value.activate_node.assert_called_once()

    @mock.patch('cmframework.agent.cmagent.cmmanage.CMManage')
    @mock.patch('cmframework.agent.cmagent.cmlogger.CMLogger')
    @mock.patch('cmframework.agent.cmagent.socket.gethostbyname')
    @mock.patch('cmframework.agent.cmagent.CMAgent._reboot_node')
    @mock.patch('cmframework.agent.cmagent.VerboseLogger')
    @mock.patch('cmframework.agent.cmagent.logging')
    def test_activate_fails(self, mock_logging, mock_verboselogger, mock_reboot_node,
                            mock_socket_get_hostbyname, mock_cmlogger, mock_cmmanage):
        mock_cmmanage.return_value.activate_node = mock.MagicMock()
        mock_cmmanage.return_value.activate_node.side_effect = CMError('Test error')

        args = []
        agent = CMAgent()
        try:
            agent(args)
            assert False
        except CMError:
            pass

        # TODO assert that alarm was raised


if __name__ == '__main__':
    unittest.main()
