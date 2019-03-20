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

import mock
from cmframework.utils.cmlogger import CMMaskFormatter


class Test(object):

    def test_masking_case1(self):
        record = r'\"compute-3\": {\"hwmgmt\": {\"password\": \"secret\"'
        formatter = mock.MagicMock()
        formatter.format.return_value = record
        maskformatter = CMMaskFormatter(formatter, ['password', 'admin_pass'])
        log = maskformatter.format(record)
        assert log == r'\"compute-3\": {\"hwmgmt\": {\"password\": \"*** password ***\"'

    def test_masking_case2(self):
        record = r'"compute-3": {"hwmgmt": {"password": "secret"'
        formatter = mock.MagicMock()
        formatter.format.return_value = record
        maskformatter = CMMaskFormatter(formatter, ['password', 'admin_pass'])
        log = maskformatter.format(record)
        assert log == r'"compute-3": {"hwmgmt": {"password": "*** password ***"'

    def test_masking_case3(self):
        record = r'\\"compute-3\\": {\\"hwmgmt\\": {\\"password\\": \\"secret\\"'
        formatter = mock.MagicMock()
        formatter.format.return_value = record
        maskformatter = CMMaskFormatter(formatter, ['password', 'admin_pass'])
        log = maskformatter.format(record)
        assert log == r'\\"compute-3\\": {\\"hwmgmt\\": {\\"password\\": \\"*** password ***\\"'
