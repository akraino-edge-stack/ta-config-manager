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

from cmframework.apis.cmupdate import CMUpdate
from cmframework.lib.cmupdateimpl import CMUpdateImpl
from cmframework.apis.cmerror import CMError


class CMUpdateImplTest(unittest.TestCase):
    @mock.patch('cmframework.lib.cmupdateimpl.CMPluginLoader')
    @mock.patch('cmframework.lib.cmupdateimpl.CMManage')
    @mock.patch('cmframework.lib.cmupdateimpl.logging')
    def test_init(self, mock_logging, mock_client, mock_pluginloader):
        mock_pluginloader.return_value.load.return_value = ({}, None)

        updater = CMUpdate('test_plugin_path', 'test_server_ip', 'test_server_port',
                           'test_client_lib_impl_module', 'test_verbose_logger')

        mock_pluginloader.assert_called_once_with('test_plugin_path')
        mock_client.assert_called_once_with('test_server_ip',
                                            'test_server_port',
                                            'test_client_lib_impl_module',
                                            'test_verbose_logger')

    @staticmethod
    def _test__read_dependency_file_incorrect(file_name):
        if file_name == 'test_plugin_path/test_handler_a.deps':
            return ([], ['x'])
        if file_name == 'test_plugin_path/test_handler_b.deps':
            return (['y'], [])

    @mock.patch.object(CMUpdateImpl, '_read_dependency_file')
    @mock.patch('cmframework.lib.cmupdateimpl.CMPluginLoader')
    @mock.patch('cmframework.lib.cmupdateimpl.CMManage')
    @mock.patch('cmframework.lib.cmupdateimpl.logging')
    def test_init_missing_handler_in_dependencies(self,
                                                  mock_logging,
                                                  mock_client,
                                                  mock_pluginloader,
                                                  mock__read_dependency_file):
        mock_pluginloader.return_value.load.return_value = ({}, None)
        mock__read_dependency_file.side_effect = \
            CMUpdateImplTest._test__read_dependency_file_incorrect

        test_handler_a_module = mock.MagicMock()
        test_handler_a_class = mock.MagicMock()
        test_handler_a_class.return_value.__str__.return_value = 'test_handler_a'
        setattr(test_handler_a_module, 'test_handler_a', test_handler_a_class)

        mock_pluginloader.return_value.load.return_value = \
            ({'test_handler_a': test_handler_a_module}, None)

        with self.assertRaises(CMError) as context:
            updater = CMUpdate('test_plugin_path', 'test_server_ip', 'test_server_port',
                               'test_client_lib_impl_module', 'test_verbose_logger')

        test_handler_b_module = mock.MagicMock()
        test_handler_b_class = mock.MagicMock()
        test_handler_b_class.return_value.__str__.return_value = 'test_handler_b'
        setattr(test_handler_b_module, 'test_handler_b', test_handler_b_class)

        mock_pluginloader.return_value.load.return_value = \
            ({'test_handler_b': test_handler_b_module}, None)

        with self.assertRaises(CMError) as context:
            updater = CMUpdate('test_plugin_path', 'test_server_ip', 'test_server_port',
                               'test_client_lib_impl_module', 'test_verbose_logger')

        mock_client.assert_not_called()

    @staticmethod
    def _test__read_dependency_file(file_name):
        if file_name == 'test_plugin_path/test_handler_a.deps':
            return ([], ['test_handler_b'])
        if file_name == 'test_plugin_path/test_handler_b.deps':
            return (['test_handler_a'], [])
        if file_name == 'test_plugin_path/test_handler_c.deps':
            return (['test_handler_b'], ['test_handler_a'])

    @staticmethod
    def _test_update_func_a(confman):
        CMUpdateImplTest._test_update_func_calls.append('test_handler_a')
        if str(confman) == 'raise exception':
            raise Exception('test_update_exception')

    @staticmethod
    def _test_update_func_b(confman):
        CMUpdateImplTest._test_update_func_calls.append('test_handler_b')

    @staticmethod
    def _test_update_func_c(confman):
        confman.get_config.return_value = {'test_properties': '_test_update_func_c properties'}
        CMUpdateImplTest._test_update_func_calls.append('test_handler_c')

    def _setup_test_handlers(self, mock_pluginloader, mock__read_dependency_file, mock_sorter):
        CMUpdateImplTest._test_update_func_calls = []

        test_handler_a_module = mock.MagicMock()
        test_handler_a_class = mock.MagicMock()
        test_handler_a_class.return_value.__str__.return_value = 'test_handler_a'
        test_handler_a_class.return_value.update.side_effect = CMUpdateImplTest._test_update_func_a
        setattr(test_handler_a_module, 'test_handler_a', test_handler_a_class)

        test_handler_b_module = mock.MagicMock()
        test_handler_b_class = mock.MagicMock()
        test_handler_b_class.return_value.__str__.return_value = 'test_handler_b'
        test_handler_b_class.return_value.update.side_effect = CMUpdateImplTest._test_update_func_b
        setattr(test_handler_b_module, 'test_handler_b', test_handler_b_class)

        test_handler_c_module = mock.MagicMock()
        test_handler_c_class = mock.MagicMock()
        test_handler_c_class.return_value.__str__.return_value = 'test_handler_c'
        test_handler_c_class.return_value.update.side_effect = CMUpdateImplTest._test_update_func_c
        setattr(test_handler_c_module, 'test_handler_c', test_handler_c_class)

        mock_pluginloader.return_value.load.return_value = \
            ({'test_handler_a': test_handler_a_module,
              'test_handler_b': test_handler_b_module,
              'test_handler_c': test_handler_c_module}, None)

        mock__read_dependency_file.side_effect = CMUpdateImplTest._test__read_dependency_file

        mock_sorter.return_value.sort.return_value = ['test_handler_c',
                                                      'test_handler_a',
                                                      'test_handler_b']

        return (test_handler_a_class, test_handler_b_class, test_handler_c_class)

    @mock.patch.object(CMUpdateImpl, '_read_dependency_file')
    @mock.patch('cmframework.lib.cmupdateimpl.CMDependencySort')
    @mock.patch('cmframework.lib.cmupdateimpl.CMPluginLoader')
    @mock.patch('cmframework.lib.cmupdateimpl.CMManage')
    @mock.patch('cmframework.lib.cmupdateimpl.logging')
    def test_update(self,
                    mock_logging,
                    mock_client,
                    mock_pluginloader,
                    mock_sorter,
                    mock__read_dependency_file):
        test_handler_a_class, test_handler_b_class, test_handler_c_class = \
            self._setup_test_handlers(mock_pluginloader, mock__read_dependency_file, mock_sorter)

        updater = CMUpdate('test_plugin_path', 'test_server_ip', 'test_server_port',
                           'test_client_lib_impl_module', 'test_verbose_logger')

        mock_confman = mock.MagicMock()
        mock_confman.__str__.return_value = 'confman'
        mock_confman.get_config.return_value = {'test_properties': 'some properties'}

        updater.update(mock_confman)

        sorter_after_graph = mock_sorter.call_args[0][0]
        assert len(sorter_after_graph) == 3
        assert 'test_handler_a' in sorter_after_graph
        assert 'test_handler_b' in sorter_after_graph
        assert 'test_handler_c' in sorter_after_graph
        assert sorter_after_graph['test_handler_a'] == ['test_handler_b']
        assert sorter_after_graph['test_handler_b'] == []
        assert sorter_after_graph['test_handler_c'] == ['test_handler_a']

        sorter_before_graph = mock_sorter.call_args[0][1]
        assert len(sorter_before_graph) == 3
        assert 'test_handler_a' in sorter_before_graph
        assert 'test_handler_b' in sorter_before_graph
        assert 'test_handler_c' in sorter_before_graph
        assert sorter_before_graph['test_handler_a'] == []
        assert sorter_before_graph['test_handler_b'] == ['test_handler_a']
        assert sorter_before_graph['test_handler_c'] == ['test_handler_b']

        mock_sorter.return_value.sort.assert_called_once()

        test_handler_a_class.return_value.update.assert_called_once_with(mock_confman)
        test_handler_b_class.return_value.update.assert_called_once_with(mock_confman)
        test_handler_c_class.return_value.update.assert_called_once_with(mock_confman)

        assert CMUpdateImplTest._test_update_func_calls == \
            mock_sorter.return_value.sort.return_value

        mock_client.return_value.set_properties.assert_called_once_with(
            {'test_properties': '_test_update_func_c properties'}, True)

    @mock.patch.object(CMUpdateImpl, '_read_dependency_file')
    @mock.patch('cmframework.lib.cmupdateimpl.ConfigManager')
    @mock.patch('cmframework.lib.cmupdateimpl.CMDependencySort')
    @mock.patch('cmframework.lib.cmupdateimpl.CMPluginLoader')
    @mock.patch('cmframework.lib.cmupdateimpl.CMManage')
    @mock.patch('cmframework.lib.cmupdateimpl.logging')
    def test_update_no_confman(self,
                               mock_logging,
                               mock_client,
                               mock_pluginloader,
                               mock_sorter,
                               mock_configmanager,
                               mock__read_dependency_file):
        test_handler_a_class, test_handler_b_class, test_handler_c_class = \
            self._setup_test_handlers(mock_pluginloader, mock__read_dependency_file, mock_sorter)

        updater = CMUpdate('test_plugin_path', 'test_server_ip', 'test_server_port',
                           'test_client_lib_impl_module', 'test_verbose_logger')

        updater.update()

        test_handler_a_class.return_value.update.assert_called_once_with(
            mock_configmanager.return_value)
        test_handler_b_class.return_value.update.assert_called_once_with(
            mock_configmanager.return_value)
        test_handler_c_class.return_value.update.assert_called_once_with(
            mock_configmanager.return_value)

        '''
        mock_configmanager.assert_called_once_with(
            mock_client.return_value.get_properties.return_value)
        '''

        assert CMUpdateImplTest._test_update_func_calls == \
            mock_sorter.return_value.sort.return_value

    @mock.patch.object(CMUpdateImpl, '_read_dependency_file')
    @mock.patch('cmframework.lib.cmupdateimpl.ConfigManager')
    @mock.patch('cmframework.lib.cmupdateimpl.CMDependencySort')
    @mock.patch('cmframework.lib.cmupdateimpl.CMPluginLoader')
    @mock.patch('cmframework.lib.cmupdateimpl.CMManage')
    @mock.patch('cmframework.lib.cmupdateimpl.logging')
    def test_update_exception(self,
                              mock_logging,
                              mock_client,
                              mock_pluginloader,
                              mock_sorter,
                              mock_configmanager,
                              mock__read_dependency_file):
        test_handler_a_class, test_handler_b_class, test_handler_c_class = \
            self._setup_test_handlers(mock_pluginloader, mock__read_dependency_file, mock_sorter)

        updater = CMUpdate('test_plugin_path', 'test_server_ip', 'test_server_port',
                           'test_client_lib_impl_module', 'test_verbose_logger')

        mock_confman = mock.MagicMock()
        mock_confman.__str__.return_value = 'raise exception'

        with self.assertRaises(Exception) as context:
            updater.update(mock_confman)

        # TODO:verify plugin(s) before exception are called.
        mock_logging.warning.assert_called_with('Update handler %s failed: %s',
                                                'test_handler_a',
                                                'test_update_exception')

    @mock.patch('cmframework.lib.cmupdateimpl.logging')
    def test_dependency_files(self, mock_logging):
        with mock.patch('cmframework.lib.cmupdateimpl.open', create=True) as mock_open:
            mock_open.return_value = mock.MagicMock(spec=file)
            file_handle = mock_open.return_value.__enter__.return_value

            file_handle.readline.side_effect = IOError('File not found')
            before, after = CMUpdateImpl._read_dependency_file('testexception: not existing')
            assert before == []
            assert after == []
            mock_logging.debug.assert_called_with('Dependency file %s not found.',
                                                  'testexception: not existing')

            file_handle.readline.side_effect = [None]
            before, after = CMUpdateImpl._read_dependency_file('./test_deps/1.deps')
            assert before == []
            assert after == []

            file_handle.readline.side_effect = ['foo', 'bar', None]
            before, after = CMUpdateImpl._read_dependency_file('./test_deps/1.deps')
            assert before == []
            assert after == []

            file_handle.readline.side_effect = ['Before: a, b', 'After: c, d', None]
            before, after = CMUpdateImpl._read_dependency_file('./test_deps/1.deps')
            assert before == ['a', 'b']
            assert after == ['c', 'd']

            file_handle.readline.side_effect = ['foo',
                                                'Before: a, b',
                                                'bar',
                                                'After: c, d',
                                                'something',
                                                None]
            before, after = CMUpdateImpl._read_dependency_file('./test_deps/1.deps')
            assert before == ['a', 'b']
            assert after == ['c', 'd']

            file_handle.readline.side_effect = ['After: c, d', 'Before: a, b', None]
            before, after = CMUpdateImpl._read_dependency_file('./test_deps/1.deps')
            assert before == ['a', 'b']
            assert after == ['c', 'd']

            file_handle.readline.side_effect = ['Before:a,b', 'After:c,d', None]
            before, after = CMUpdateImpl._read_dependency_file('./test_deps/1.deps')
            assert before == ['a', 'b']
            assert after == ['c', 'd']

            file_handle.readline.side_effect = ['Before:  a,  b  ', 'After:   c,    d   ', None]
            before, after = CMUpdateImpl._read_dependency_file('./test_deps/1.deps')
            assert before == ['a', 'b']
            assert after == ['c', 'd']

if __name__ == '__main__':
    unittest.main()
