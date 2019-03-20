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
import os
from cmframework.utils import cmtopologicalsort


class AnsiblePlaybooks(object):
    bootstrapping_playbook = 'bootstrapping-playbook.yml'
    provisioning_playbook = 'provisioning-playbook.yml'
    postconfig_playbook = 'postconfig-playbook.yml'
    finalize_playbook = 'finalize-playbook.yml'

    def __init__(self, dest, bootstrapping_path, provisioning_path, postconfig_path, finalize_path):
        self.dest = dest
        self.bootstrapping_path = bootstrapping_path
        self.provisioning_path = provisioning_path
        self.postconfig_path = postconfig_path
        self.finalize_path = finalize_path

    def generate_playbooks(self):
        self._generate_playbook(self.bootstrapping_path, self.bootstrapping_playbook)
        self._generate_playbook(self.provisioning_path, self.provisioning_playbook)
        self._generate_playbook(self.postconfig_path, self.postconfig_playbook)
        self._generate_playbook(self.finalize_path, self.finalize_playbook)

    def _generate_playbook(self, directory, name):
        graph = self._get_dependency_graph(directory)
        topsort = cmtopologicalsort.TopSort(graph)
        sortedlists = topsort.sort()
        with open(self.dest + '/' + name, 'w') as f:
            for entry in sortedlists:
                for e in entry:
                    fullpath = directory + '/' + e
                    if os.path.exists(fullpath):
                        f.write('- import_playbook: ' + e + '\n')

    def _get_dependency_graph(self, directory):
        entries = os.listdir(directory)
        graph = {}
        for entry in entries:
            entryfull = directory + '/' + entry
            if os.path.isfile(entryfull) or os.path.islink(entryfull):
                requires = self._get_required_playbooks(entryfull)
                graph[entry] = requires
        return graph

    @staticmethod
    def _get_required_playbooks(playbook):
        requires = []
        with open(playbook) as f:
            lines = f.read().splitlines()
            # parse the lines containing:
            # cmframework.requires: <comma separated list of playbooks>
            for line in lines:
                if 'cmframework.requires:' in line:
                    data = line.split(':')
                    if len(data) != 2:
                        continue
                    tmp = data[1].replace(" ", "")
                    requires = tmp.split(',')
                    break
        return requires


if __name__ == '__main__':
    playbooks = AnsiblePlaybooks('/tmp/', '/etc/lcm/playbooks/installation/bootstrapping',
                                 '/etc/lcm/playbooks/installation/provisioning',
                                 '/etc/lcm/playbooks/installation/postconfig',
                                 '/etc/lcm/playbooks/installation/finalize')
    playbooks.generate_playbooks()
