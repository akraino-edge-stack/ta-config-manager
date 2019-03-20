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
from collections import OrderedDict

from cmframework.utils.cmdsshandler import CMDSSHandler
from cmframework.apis.cmerror import CMError
from dss.api import dss_error


class CMDSSHandlerTest(unittest.TestCase):
    @mock.patch('cmframework.utils.cmdsshandler.dss_client.Client')
    @mock.patch('cmframework.utils.cmdsshandler.logging')
    def test_init(self, mock_logging, mock_dss_client):
        handler = CMDSSHandler(uri='test_uri')

        mock_dss_client.assert_called_once_with('test_uri')

    @mock.patch('cmframework.utils.cmdsshandler.dss_client.Client')
    @mock.patch('cmframework.utils.cmdsshandler.logging')
    def test_get_domains_exception(self, mock_logging, mock_dss_client):
        handler = CMDSSHandler(uri='test_uri')

        mock_dss_client.return_value.get_domains.side_effect = dss_error.Error('no domains')

        with self.assertRaises(CMError) as context:
            handler.get_domains()

    @mock.patch('cmframework.utils.cmdsshandler.dss_client.Client')
    @mock.patch('cmframework.utils.cmdsshandler.logging')
    def test_get_domains(self, mock_logging, mock_dss_client):
        handler = CMDSSHandler(uri='test_uri')

        expected_result = ['a domain', 'b domain', 'c domain']
        mock_dss_client.return_value.get_domains.return_value = expected_result

        domains = handler.get_domains()

        assert domains == expected_result

    @mock.patch('cmframework.utils.cmdsshandler.dss_client.Client')
    @mock.patch('cmframework.utils.cmdsshandler.logging')
    def test_get_domain_not_existing(self, mock_logging, mock_dss_client):
        handler = CMDSSHandler(uri='test_uri')

        mock_dss_client.return_value.get_domains.return_value = ['a domain', 'b domain', 'c domain']

        domain = handler.get_domain('not domain')

        assert domain is None

        mock_dss_client.return_value.get_domains.assert_called_once()
        mock_dss_client.return_value.get_domain.assert_not_called()

    @mock.patch('cmframework.utils.cmdsshandler.dss_client.Client')
    @mock.patch('cmframework.utils.cmdsshandler.logging')
    def test_get_domain_dss_fails(self, mock_logging, mock_dss_client):
        handler = CMDSSHandler(uri='test_uri')

        mock_dss_client.return_value.get_domains.return_value = ['a domain', 'b domain', 'c domain']
        mock_dss_client.return_value.get_domain.side_effect = dss_error.Error('some error')

        with self.assertRaises(CMError) as context:
            domain = handler.get_domain('a domain')

        mock_dss_client.return_value.get_domains.assert_called_once()
        mock_dss_client.return_value.get_domain.assert_called_once_with('a domain')

    @mock.patch('cmframework.utils.cmdsshandler.dss_client.Client')
    @mock.patch('cmframework.utils.cmdsshandler.logging')
    def test_get_domain(self, mock_logging, mock_dss_client):
        handler = CMDSSHandler(uri='test_uri')

        mock_dss_client.return_value.get_domains.return_value = ['a domain', 'b domain', 'c domain']

        expected_result = OrderedDict([('name1', 'value1'), ('name2', 'value2')])
        mock_dss_client.return_value.get_domain.return_value = expected_result

        domain = handler.get_domain('a domain')

        assert domain == expected_result

    @mock.patch('cmframework.utils.cmdsshandler.dss_client.Client')
    @mock.patch('cmframework.utils.cmdsshandler.logging')
    def test_set_dss_fails(self, mock_logging, mock_dss_client):
        handler = CMDSSHandler(uri='test_uri')

        mock_dss_client.return_value.set.side_effect = dss_error.Error('some error')

        with self.assertRaises(CMError) as context:
            handler.set('a domain', 'a name', 'a value')

        mock_dss_client.return_value.set.assert_called_once_with('a domain', 'a name', 'a value')

    @mock.patch('cmframework.utils.cmdsshandler.dss_client.Client')
    @mock.patch('cmframework.utils.cmdsshandler.logging')
    def test_set(self, mock_logging, mock_dss_client):
        handler = CMDSSHandler(uri='test_uri')

        handler.set('a domain', 'a name', 'a value')

        mock_dss_client.return_value.set.assert_called_once_with('a domain', 'a name', 'a value')

    @mock.patch('cmframework.utils.cmdsshandler.dss_client.Client')
    @mock.patch('cmframework.utils.cmdsshandler.logging')
    def test_delete_dss_fails(self, mock_logging, mock_dss_client):
        handler = CMDSSHandler(uri='test_uri')

        mock_dss_client.return_value.get_domains.return_value = ['a domain', 'b domain', 'c domain']

        mock_dss_client.return_value.get_domain.return_value = OrderedDict([('name', 'value')])

        mock_dss_client.return_value.delete.side_effect = dss_error.Error('some error')

        with self.assertRaises(CMError) as context:
            handler.delete('a domain', 'name')

        mock_dss_client.return_value.delete.assert_called_once_with('a domain', 'name')

    @mock.patch('cmframework.utils.cmdsshandler.dss_client.Client')
    @mock.patch('cmframework.utils.cmdsshandler.logging')
    def test_delete_non_existing_name(self, mock_logging, mock_dss_client):
        handler = CMDSSHandler(uri='test_uri')

        mock_dss_client.return_value.get_domains.return_value = ['a domain', 'b domain', 'c domain']

        mock_dss_client.return_value.get_domain.return_value = OrderedDict([('name', 'value')])

        handler.delete('a domain', 'a name')

        mock_dss_client.return_value.get_domain.assert_called_once_with('a domain')
        mock_dss_client.return_value.delete.assert_not_called()

    @mock.patch('cmframework.utils.cmdsshandler.dss_client.Client')
    @mock.patch('cmframework.utils.cmdsshandler.logging')
    def test_delete_non_existing_domain(self, mock_logging, mock_dss_client):
        handler = CMDSSHandler(uri='test_uri')

        mock_dss_client.return_value.get_domains.return_value = ['a domain', 'b domain', 'c domain']

        handler.delete('not domain', 'no name')

        mock_dss_client.return_value.get_domains.assert_called_once()
        mock_dss_client.return_value.get_domain.assert_not_called()
        mock_dss_client.return_value.delete.assert_not_called()

    @mock.patch('cmframework.utils.cmdsshandler.dss_client.Client')
    @mock.patch('cmframework.utils.cmdsshandler.logging')
    def test_get_dss_fails(self, mock_logging, mock_dss_client):
        handler = CMDSSHandler(uri='test_uri')

        mock_dss_client.return_value.get_domains.return_value = ['a domain', 'b domain', 'c domain']

        mock_dss_client.return_value.get_domain.side_effect = dss_error.Error('some error')

        with self.assertRaises(CMError) as context:
            handler.get('a domain', 'name')

        mock_dss_client.return_value.get_domain.assert_called_once_with('a domain')

    @mock.patch('cmframework.utils.cmdsshandler.dss_client.Client')
    @mock.patch('cmframework.utils.cmdsshandler.logging')
    def test_get_non_existing_name(self, mock_logging, mock_dss_client):
        handler = CMDSSHandler(uri='test_uri')

        mock_dss_client.return_value.get_domains.return_value = ['a domain', 'b domain', 'c domain']
        mock_dss_client.return_value.get_domain.return_value = OrderedDict([('name', 'value')])

        value = handler.get('a domain', 'a name')

        assert value is None

        mock_dss_client.return_value.get_domain.assert_called_once_with('a domain')

    @mock.patch('cmframework.utils.cmdsshandler.dss_client.Client')
    @mock.patch('cmframework.utils.cmdsshandler.logging')
    def test_get_non_existing_domain(self, mock_logging, mock_dss_client):
        handler = CMDSSHandler(uri='test_uri')

        mock_dss_client.return_value.get_domains.return_value = ['a domain', 'b domain', 'c domain']
        mock_dss_client.return_value.get_domain.return_value = OrderedDict([('name', 'value')])

        value = handler.get('some domain', 'a name')

        assert value is None

        mock_dss_client.return_value.get_domain.assert_not_called()
        mock_dss_client.return_value.get_domains.assert_called_once()

    @mock.patch('cmframework.utils.cmdsshandler.dss_client.Client')
    @mock.patch('cmframework.utils.cmdsshandler.logging')
    def test_get(self, mock_logging, mock_dss_client):
        handler = CMDSSHandler(uri='test_uri')

        mock_dss_client.return_value.get_domains.return_value = ['a domain', 'b domain', 'c domain']
        mock_dss_client.return_value.get_domain.return_value = OrderedDict([('name', 'value')])

        value = handler.get('a domain', 'name')

        assert value == 'value'

    @mock.patch('cmframework.utils.cmdsshandler.dss_client.Client')
    @mock.patch('cmframework.utils.cmdsshandler.logging')
    def test_delete_domain_dss_fails(self, mock_logging, mock_dss_client):
        handler = CMDSSHandler(uri='test_uri')

        mock_dss_client.return_value.get_domains.return_value = ['a domain', 'b domain', 'c domain']

        mock_dss_client.return_value.delete_domain.side_effect = dss_error.Error('some error')

        with self.assertRaises(CMError) as context:
            handler.delete_domain('a domain')

        mock_dss_client.return_value.delete_domain.assert_called_once_with('a domain')

    @mock.patch('cmframework.utils.cmdsshandler.dss_client.Client')
    @mock.patch('cmframework.utils.cmdsshandler.logging')
    def test_delete_domain_non_existent(self, mock_logging, mock_dss_client):
        handler = CMDSSHandler(uri='test_uri')

        mock_dss_client.return_value.get_domains.return_value = ['a domain', 'b domain', 'c domain']

        handler.delete_domain('not domain')

        mock_dss_client.return_value.get_domains.assert_called_once()
        mock_dss_client.return_value.delete_domain.assert_not_called()

    @mock.patch('cmframework.utils.cmdsshandler.dss_client.Client')
    @mock.patch('cmframework.utils.cmdsshandler.logging')
    def test_delete_domain(self, mock_logging, mock_dss_client):
        handler = CMDSSHandler(uri='test_uri')

        mock_dss_client.return_value.get_domains.return_value = ['a domain', 'b domain', 'c domain']

        handler.delete_domain('a domain')

        mock_dss_client.return_value.get_domains.assert_called_once()
        mock_dss_client.return_value.delete_domain.assert_called_once_with('a domain')


if __name__ == '__main__':
    unittest.main()
