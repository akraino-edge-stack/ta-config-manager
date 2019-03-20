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

from cmframework.apis.cmerror import CMError


class CMDependencySort(object):
    def __init__(self, after=None, before=None):
        if not after:
            after = {}
        if not before:
            before = {}

        self._entries = set()
        self._before = before

        self._convert_after_to_before(after)
        self._find_all_entries()

        self._sorted_entries = []

    def _convert_after_to_before(self, after):
        for entry, deps in after.iteritems():
            self._entries.add(entry)
            for dep in deps:
                dep_before = self._before.get(dep, None)
                if not dep_before:
                    dep_before = []
                    self._before[dep] = dep_before
                if entry not in dep_before:
                    dep_before.append(entry)

    def _find_all_entries(self):
        for entry, deps in self._before.iteritems():
            self._entries.add(entry)
            for dep in deps:
                self._entries.add(dep)

    def sort(self):
        self._sort_entries()
        return self._sorted_entries

    def _sort_entries(self):
        sorted_list = []
        permanent_mark_list = []
        for entry in self._entries:
            if entry not in permanent_mark_list:
                self._visit(entry, sorted_list, permanent_mark_list)
        self._sorted_entries = sorted_list

    def _visit(self, entry, sorted_list, permanent_mark_list, temporary_mark_list=None):
        if not temporary_mark_list:
            temporary_mark_list = []

        if entry in permanent_mark_list:
            return

        if entry in temporary_mark_list:
            raise CMError('Cycle detected in dependencies ({})'.format(entry))

        temporary_mark_list.append(entry)
        for dep in self._before.get(entry, []):
            self._visit(dep, sorted_list, permanent_mark_list, temporary_mark_list)
        permanent_mark_list.append(entry)
        sorted_list.insert(0, entry)
