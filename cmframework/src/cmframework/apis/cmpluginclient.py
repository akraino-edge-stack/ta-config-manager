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


class CMPluginClient(object):
    # pylint: disable=no-self-use, unused-argument
    def get_property(self, prop_name):
        """read the value assoicated with a property

            Arguments:

            prop_name: The name of the property to be read.

            Raise:

            CMError is raised in-case of failure
        """
        raise cmerror.CMError('Not implemented')

    # pylint: disable=no-self-use, unused-argument
    def get_properties(self, prop_filter):
        """read a set of properties matching a filter.

            Arguments:

            prop_filter: A string containing the re used to match the read
                         properties.

            Raise:

            CMError is raised in-case of a failure.
        """
        raise cmerror.CMError('Not implemented')

    # pylint: disable=no-self-use, unused-argument
    def set_property(self, name, value):
        raise cmerror.CMError('Not implemented')
