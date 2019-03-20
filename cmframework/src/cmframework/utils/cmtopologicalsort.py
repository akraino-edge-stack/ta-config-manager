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
from __future__ import print_function
from cmframework.apis import cmerror


class TopSort(object):
    """
    This class implements a topological sort algorithm.

    It expects a dependency graph as an input and returns a sorted list as an
    output. The returned list contains lists sorted accordingly to the dependency
    graph:

    Usage Example:
        # The following graph indicates that 2 depends on 11, 9 depends on 11,8,10 and so on...
        graph = {2: [11],
                 9: [11, 8, 10],
                10: [11, 3],
                11: [7, 5],
                8: [7, 3]}

        sort = TopSort(graph)
        try:
            sorted = sort.sort()
            for entry in sorted:
                print('%r' % entry)
        except cmerror.CMError as exp:
           print('Got exception %s' % str(exp))

    The above example will generate the following output:
    [3, 5, 7]
    [8, 11]
    [2, 10]
    [9]
    """

    def __init__(self, graph):
        self.graph = graph
        self.output = {}
        self.recursionlevel = 0

    def _get_dependent_entries(self, entry):
        result = []
        for e, deps in self.graph.iteritems():
            if entry in deps:
                result.append(e)
        return result

    def _update_dependent_entries(self, entry):
        maximumrecursion = (len(self.graph)) * (len(self.graph))
        if (self.recursionlevel + 1) >= maximumrecursion:
            raise cmerror.CMError('cyclic dependency detected, graph %r' % self.graph)
        self.recursionlevel += 1
        dependententries = self._get_dependent_entries(entry)
        entrydepth = self.output[entry]
        for e in dependententries:
            if e in self.output:
                if entrydepth >= self.output[e]:
                    self.output[e] = entrydepth + 1
                    self._update_dependent_entries(e)

    def sort(self):
        for entry, deps in self.graph.iteritems():
            depth = 0
            if entry in self.output:
                depth = self.output[entry]

            # calculate new depth according to dependencies
            newdepth = depth
            for dep in deps:
                if dep in self.output:
                    weight = self.output[dep]
                else:
                    weight = 0
                    self.output[dep] = 0
                if weight >= newdepth:
                    newdepth = weight + 1

            # if our depth is changed we need to update the entries depending on us
            self.output[entry] = newdepth
            if newdepth > depth and entry in self.output:
                self.recursionlevel = 0
                self._update_dependent_entries(entry)

        return self._getsorted()

    def _getsorted(self):
        import operator
        sortedoutput = sorted(self.output.items(), key=operator.itemgetter(1))
        result = {}
        for entry in sortedoutput:
            if entry[1] not in result:
                result[entry[1]] = []
            result[entry[1]].append(entry[0])

        returned = []
        for entry, data in result.iteritems():
            returned.append(data)

        return returned


def main():
    graph1 = {2: [11],
              9: [11, 8, 10],
              10: [11, 3],
              11: [7, 5],
              8: [7, 3]}

    graph2 = {'playbook2.yaml': [], 'playbook1.yaml': ['playbook2.yaml']}

    topsort1 = TopSort(graph1)
    topsort2 = TopSort(graph2)

    try:
        print(graph1)
        sortedlists1 = topsort1.sort()
        for entry in sortedlists1:
            print('%r' % entry)

        print(graph2)
        sortedlists2 = topsort2.sort()
        for entry in sortedlists2:
            print('%r' % entry)
    except cmerror.CMError as exp:
        print(str(exp))


if __name__ == '__main__':
    main()
