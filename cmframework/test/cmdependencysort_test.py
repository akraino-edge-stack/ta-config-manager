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

from cmframework.utils.cmdependencysort import CMDependencySort as Sort
from cmframework.apis.cmerror import CMError


class CMDependencySortTest(unittest.TestCase):
    def test_empty(self):
        sort = Sort()
        sorted_list = sort.sort()
        assert sorted_list == []

    def test_one_no_deps(self):
        sort = Sort({'a': []})
        sorted_list = sort.sort()
        assert sorted_list == ['a']

        sort = Sort(None, {'a': []})
        sorted_list = sort.sort()
        assert sorted_list == ['a']

    def test_both_no_deps(self):
        sort = Sort({'a': []}, {'a': []})
        sorted_list = sort.sort()
        assert sorted_list == ['a']

        sort = Sort({'a': [], 'b': []}, {'a': [], 'b': []})
        sorted_list = sort.sort()

        assert len(sorted_list) == 2
        assert 'a' in sorted_list
        assert 'b' in sorted_list

    @staticmethod
    def _assert_orderings(after, before, sorted_list):
        for entry, deps in after.iteritems():
            for dep in deps:
                assert sorted_list.index(entry) > sorted_list.index(dep)

        for entry, deps in before.iteritems():
            for dep in deps:
                assert sorted_list.index(entry) < sorted_list.index(dep)

    def test_mandbc(self):
        after = {'a': ['m'], 'b': ['d']}
        before = {'a': ['b', 'c', 'd', 'n'], 'b': ['c']}
        sort = Sort(after, before)
        sorted_list = sort.sort()

        CMDependencySortTest._assert_orderings(after, before, sorted_list)

    def test_simple_only_after(self):
        after = {'a': ['b'], 'b': ['c']}
        before = {}
        sort = Sort(after)
        sorted_list = sort.sort()

        CMDependencySortTest._assert_orderings(after, before, sorted_list)

    def test_simple_only_before(self):
        after = {}
        before = {'a': ['b'], 'b': ['c']}
        sort = Sort(None, before)
        sorted_list = sort.sort()

        CMDependencySortTest._assert_orderings(after, before, sorted_list)

    def test_simple(self):
        after = {'b': ['a'], 'c': ['b']}
        before = {'a': ['b'], 'b': ['c']}
        sort = Sort(after, before)
        sorted_list = sort.sort()

        CMDependencySortTest._assert_orderings(after, before, sorted_list)

    def test_cycle_before_after(self):
        after = {'b': ['a']}
        before = {'b': ['a']}
        sort = Sort(after, before)

        with self.assertRaises(CMError) as context:
            sorted_list = sort.sort()

    def test_cycle_only_before(self):
        after = {}
        before = {'b': ['a'], 'a': ['b']}
        sort = Sort(after, before)

        with self.assertRaises(CMError) as context:
            sorted_list = sort.sort()

    def test_cycle_only_after(self):
        after = {'b': ['a'], 'a': ['b']}
        before = {}
        sort = Sort(after, before)

        with self.assertRaises(CMError) as context:
            sorted_list = sort.sort()

if __name__ == '__main__':
    unittest.main()
