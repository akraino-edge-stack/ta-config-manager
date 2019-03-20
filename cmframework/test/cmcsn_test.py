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

from cmframework.server.cmcsn import CMCSN
from cmframework.apis.cmerror import CMError


class CMCSNTest(unittest.TestCase):
    @mock.patch('cmframework.server.cmcsn.logging')
    def test_initial_config(self, mock_logging):
        mock_backend = mock.MagicMock()
        mock_backend.get_property = mock.MagicMock()
        mock_backend.get_property.side_effect = CMError('Test error')

        csn = CMCSN(mock_backend)

        mock_backend.assert_has_calls([call.get_property('cloud.cmframework')])
        self.assertEqual(csn.get(), 0)

    @mock.patch('cmframework.server.cmcsn.logging')
    def test_bad_config(self, mock_logging):
        mock_backend = mock.MagicMock()
        mock_backend.get_property = mock.MagicMock()
        mock_backend.get_property.return_value = 'bad json'

        csn = CMCSN(mock_backend)

        mock_backend.assert_has_calls([call.get_property('cloud.cmframework')])
        self.assertEqual(csn.get(), 0)

    @mock.patch('cmframework.server.cmcsn.logging')
    def test_old_config(self, mock_logging):
        mock_backend = mock.MagicMock()
        mock_backend.get_property = mock.MagicMock()
        mock_backend.get_property.return_value = ('{"csn": {"global": 101, "nodes": '
                                                  '{"node-a": 99, "node-b": 100, "node-c": 101}}}')

        csn = CMCSN(mock_backend)

        self.assertEqual(csn.get(), 101)
        self.assertEqual(csn.get_node_csn('node-a'), 99)
        self.assertEqual(csn.get_node_csn('node-b'), 100)
        self.assertEqual(csn.get_node_csn('node-c'), 101)

    @mock.patch('cmframework.server.cmcsn.logging')
    def test_increment(self, mock_logging):
        mock_backend = mock.MagicMock()
        mock_backend.get_property = mock.MagicMock()
        mock_backend.set_property = mock.MagicMock()
        mock_backend.get_property.return_value = ('{"csn": {"global": 101, "nodes": '
                                                  '{"node-a": 99, "node-b": 100, "node-c": 101}}}')

        csn = CMCSN(mock_backend)
        csn.increment()

        mock_backend.set_property.assert_called_once()
        mock_backend_set_property_arg_value = json.loads(mock_backend.set_property.call_args[0][1])
        self.assertEqual(mock_backend_set_property_arg_value['csn']['global'], 102)
        self.assertEqual(mock_backend_set_property_arg_value['csn']['nodes']['node-a'], 99)
        self.assertEqual(mock_backend_set_property_arg_value['csn']['nodes']['node-b'], 100)
        self.assertEqual(mock_backend_set_property_arg_value['csn']['nodes']['node-c'], 101)

        self.assertEqual(csn.get(), 102)

    @mock.patch('cmframework.server.cmcsn.logging')
    def test_sync_node(self, mock_logging):
        mock_backend = mock.MagicMock()
        mock_backend.get_property = mock.MagicMock()
        mock_backend.set_property = mock.MagicMock()
        mock_backend.get_property.return_value = ('{"csn": {"global": 101, "nodes": '
                                                  '{"node-a": 99, "node-b": 100, "node-c": 101}}}')

        csn = CMCSN(mock_backend)
        csn.sync_node_csn('node-a')

        mock_backend.set_property.assert_called_once()
        mock_backend_set_property_arg_value = json.loads(mock_backend.set_property.call_args[0][1])
        self.assertEqual(mock_backend_set_property_arg_value['csn']['global'], 101)
        self.assertEqual(mock_backend_set_property_arg_value['csn']['nodes']['node-a'], 101)
        self.assertEqual(mock_backend_set_property_arg_value['csn']['nodes']['node-b'], 100)
        self.assertEqual(mock_backend_set_property_arg_value['csn']['nodes']['node-c'], 101)

        self.assertEqual(csn.get_node_csn('node-a'), 101)


if __name__ == '__main__':
    unittest.main()
