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


class CMBackend(object):
    # pylint: disable=no-self-use, unused-argument
    def get_property(self, prop_name):
        """get the value of some property

           Arguments:

           prop_name: The name of the property

           Raise:

           CMError is raised in-case of failure
        """
        raise cmerror.CMError('No implemented')

    # pylint: disable=no-self-use, unused-argument
    def get_properties(self, prop_filter):
        """get the properties matching some filter

           Arguments:

           prop_filter: A string containing the re used to match the required
                        properties.

            Raise:

            CMError is raised in-case of failure
        """
        raise cmerror.CMError('Not implemented')

    # pylint: disable=no-self-use, unused-argument
    def set_property(self, prop_name, prop_value):
        """set/update a value to some property

           Arguments:

           prop_name: The name of the property to be set/updated.

           prop_value: The value of the property

           Raise:

           CMError is raised in-case of failure
        """
        raise cmerror.CMError('Not implemented')

    # pylint: disable=no-self-use, unused-argument
    def set_properties(self, properties):
        """set/update a group of properties

           Arguments:

           props: A dictionary containing the changed properties.

           Raise:

           CMError is raised in-case of a failure.
        """
        raise cmerror.CMError('Not implemented')

    # pylint: disable=no-self-use, unused-argument
    def delete_property(self, prop_name):
        """delete a property

           This is the API used to delete a configuration property.

           Arguments:

           prop_name: The name of the property to be deleted.

           Raise:

           CMError is raised in-case of a failure.
        """
        raise cmerror.CMError('Not implemented')

    # pylint: disable=no-self-use, unused-argument
    def delete_properties(self, arg):
        """delete a group of properties

           Arguments:

           arg: This can be either a string representing the re used when
                matching the properties to be deleted, or it can be a list of
                properties names to be deleted.

            Rise:

            CMError is raised in-case of a failure.
        """
        raise cmerror.CMError('Not implemented')

if __name__ == '__main__':
    pass
