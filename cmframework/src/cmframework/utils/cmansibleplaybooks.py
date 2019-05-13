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
    progress_playbook = 'report_installation_progress.yml'

    def __init__(self, dest, bootstrapping_path, provisioning_path, postconfig_path, finalize_path):
        self.dest = dest
        self.bootstrapping_path = bootstrapping_path
        self.provisioning_path = provisioning_path
        self.postconfig_path = postconfig_path
        self.finalize_path = finalize_path

    def generate_playbooks(self):
        bootstrapping_lists, bootstrapping_size = self._get_playbook_lists(self.bootstrapping_path)
        provisioning_lists, provisioning_size = self._get_playbook_lists(self.provisioning_path)
        postconfig_lists, postconfig_size = self._get_playbook_lists(self.postconfig_path)
        finalize_lists, finalize_size = self._get_playbook_lists(self.finalize_path)

        number_of_playbooks = bootstrapping_size \
                              + provisioning_size \
                              + postconfig_size \
                              + finalize_size

        playbook_percentage_value = 99.0 / number_of_playbooks

        self._generate_playbook(bootstrapping_lists, self.bootstrapping_playbook, 0, playbook_percentage_value)
        progress_start = bootstrapping_size*playbook_percentage_value
        self._generate_playbook(provisioning_lists, self.provisioning_playbook, progress_start, playbook_percentage_value)
        progress_start = (bootstrapping_size+provisioning_size)*playbook_percentage_value
        self._generate_playbook(postconfig_lists, self.postconfig_playbook, progress_start, playbook_percentage_value)
        progress_start = (bootstrapping_size+provisioning_size+postconfig_size)*playbook_percentage_value
        self._generate_playbook(finalize_lists, self.finalize_playbook, progress_start, playbook_percentage_value)

    def _get_playbook_lists(self, directory):
        graph = self._get_dependency_graph(directory)
        topsort = cmtopologicalsort.TopSort(graph)
        sortedlists = topsort.sort()

        size = 0
        for entry in sortedlists:
            size += len(entry)

        return sortedlists, size

    def _generate_playbook(self, sortedlists, name, progress_start, playbook_percentage_value):
        progress = progress_start
        with open(self.dest + '/' + name, 'w') as f:
            for entry in sortedlists:
                for e in entry:
                    f.write('- import_playbook: ' + self.progress_playbook +
                            ' installation_progress_phase=' + name +
                            ' installation_progress_playbook=' + e +
                            ' installation_progress=' + str(progress) + '\n')
                    f.write('- import_playbook: ' + e + '\n')
                    progress = progress+playbook_percentage_value

    def _get_dependency_graph(self, directory):
        entries = os.listdir(directory)
        graph = {}
        for entry in entries:
            entryfull = directory + '/' + entry
            if os.path.isfile(entryfull) or os.path.islink(entryfull):
                requires = self._get_required_playbooks(entryfull)
                existing_requires = []
                for require in requires:
                    requirefull = directory + '/' + require
                    if os.path.exists(requirefull):
                        existing_requires.append(require)
                graph[entry] = existing_requires

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
