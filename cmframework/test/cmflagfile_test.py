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
from mock import mock_open
import json

from cmframework.utils.cmflagfile import CMFlagFile
from cmframework.apis.cmerror import CMError


class CMFlagFileTest(unittest.TestCase):
    @mock.patch('cmframework.utils.cmflagfile.os')
    @mock.patch('cmframework.utils.cmflagfile.logging')
    def test_is_set_for_non_existing_file(self, mock_logging, mock_os):
        mock_os.path = mock.MagicMock()
        mock_os.path.exists = mock.MagicMock()
        mock_os.path.exists.return_value = False

        flagfile = CMFlagFile('foo')
        self.assertFalse(flagfile)

    @mock.patch('cmframework.utils.cmflagfile.os')
    @mock.patch('cmframework.utils.cmflagfile.logging')
    def test_is_set_for_existing_file(self, mock_logging, mock_os):
        mock_os.path = mock.MagicMock()
        mock_os.path.exists = mock.MagicMock()
        mock_os.path.exists.return_value = True

        flagfile = CMFlagFile('foo')
        self.assertTrue(flagfile)

    @mock.patch('cmframework.utils.cmflagfile.open', new_callable=mock_open)
    @mock.patch('cmframework.utils.cmflagfile.os')
    @mock.patch('cmframework.utils.cmflagfile.logging')
    def test_set_for_nonexisting_file(self, mock_logging, mock_os, mock_file):
        mock_os.path = mock.MagicMock()
        mock_os.path.exists = mock.MagicMock()
        mock_os.path.exists.return_value = False

        flagfile = CMFlagFile('foo')
        self.assertFalse(flagfile)

        flagfile.set()

        mock_file.assert_called_with('/mnt/config-manager/foo', 'w')
        mock_file.return_value.write.assert_called_once()

    @mock.patch('cmframework.utils.cmflagfile.open', new_callable=mock_open)
    @mock.patch('cmframework.utils.cmflagfile.os')
    @mock.patch('cmframework.utils.cmflagfile.logging')
    def test_set_for_existing_file(self, mock_logging, mock_os, mock_file):
        mock_os.path = mock.MagicMock()
        mock_os.path.exists = mock.MagicMock()
        mock_os.path.exists.return_value = True

        flagfile = CMFlagFile('foo')
        self.assertTrue(flagfile)

        flagfile.set()

        mock_file.assert_not_called()

    @mock.patch('cmframework.utils.cmflagfile.open', new_callable=mock_open)
    @mock.patch('cmframework.utils.cmflagfile.os')
    @mock.patch('cmframework.utils.cmflagfile.logging')
    def test_set_io_failure(self, mock_logging, mock_os, mock_file):
        mock_os.path = mock.MagicMock()
        mock_os.path.exists = mock.MagicMock()
        mock_os.path.exists.return_value = False

        mock_file.return_value.write.side_effect = IOError()

        flagfile = CMFlagFile('foo')
        self.assertFalse(flagfile)

        with self.assertRaises(CMError) as context:
            flagfile.set()

    @mock.patch('cmframework.utils.cmflagfile.os')
    @mock.patch('cmframework.utils.cmflagfile.logging')
    def test_unset_for_existing_file(self, mock_logging, mock_os):
        mock_os.path = mock.MagicMock()
        mock_os.path.exists = mock.MagicMock()
        mock_os.path.exists.return_value = True

        flagfile = CMFlagFile('foo')
        self.assertTrue(flagfile)

        flagfile.unset()

        mock_os.remove.assert_called_once_with('/mnt/config-manager/foo')

    @mock.patch('cmframework.utils.cmflagfile.os')
    @mock.patch('cmframework.utils.cmflagfile.logging')
    def test_unset_for_nonexisting_file(self, mock_logging, mock_os):
        mock_os.path = mock.MagicMock()
        mock_os.path.exists = mock.MagicMock()
        mock_os.path.exists.return_value = False

        flagfile = CMFlagFile('foo')
        self.assertFalse(flagfile)

        flagfile.unset()

        mock_os.remove.assert_not_called()

    @mock.patch('cmframework.utils.cmflagfile.os')
    @mock.patch('cmframework.utils.cmflagfile.logging')
    def test_unset_io_failure(self, mock_logging, mock_os):
        mock_os.path = mock.MagicMock()
        mock_os.path.exists = mock.MagicMock()
        mock_os.path.exists.return_value = True

        flagfile = CMFlagFile('foo')
        self.assertTrue(flagfile)

        mock_os.remove.side_effect = IOError()

        with self.assertRaises(CMError) as context:
            flagfile.unset()

if __name__ == '__main__':
    unittest.main()
