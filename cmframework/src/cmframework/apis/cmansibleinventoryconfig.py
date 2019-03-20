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
from cmframework.apis import cmerror


class CMAnsibleInventoryConfigPlugin(object):

    def __init__(self, confman, inventory, ownhost):
        self.confman = confman
        self.inventory = inventory
        self.ownhost = ownhost

    def add_host_var(self, host, name, value):
        """add a host specific variable
           Arguments:
           host: The name of the host
           name: The name of the variable.
           value: The value
        """
        if host not in self.inventory['_meta']['hostvars']:
            self.inventory['_meta']['hostvars'][host] = {}
        self.inventory['_meta']['hostvars'][host][name] = value

    def add_global_var(self, name, value):
        """add a global variable to the inventory
           Arguments:
           name: The name of the variable
           value: The value
        """
        self.inventory['all']['vars'][name] = value

    def add_host_group(self, name, value):
        self.inventory[name] = value

    # pylint: disable=no-self-use
    def handle_bootstrapping(self):
        """provide inventory extensions

           Raise:

           CMError is raised in-case of failure
        """

        raise cmerror.CMError('No implemented')

    # pylint: disable=no-self-use
    def handle_provisioning(self):
        """provide inventory extensions

           Raise:

           CMError is raised in-case of failure
        """

        raise cmerror.CMError('No implemented')

    # pylint: disable=no-self-use
    def handle_postconfig(self):
        """provide inventory extensions

           Raise:

           CMError is raised in-case of failure
        """

        raise cmerror.CMError('No implemented')

    # pylint: disable=no-self-use
    def handle_setup(self):
        """provide inventory extensions

           Raise:

           CMError is raised in-case of failure
        """

        raise cmerror.CMError('No implemented')
