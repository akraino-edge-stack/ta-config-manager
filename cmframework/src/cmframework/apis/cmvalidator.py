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


class CMValidator(object):
    def __init__(self):
        self.plugin_client = None

    # pylint: disable=no-self-use
    def get_subscription_info(self):
        """get the subscription filter

           This API is used to get the re for matching the properties which the
           validation plugin is concerned about.

           Return:

           A string representing the regular expression used to match the
           properties which the validation plugin is concerned about.

           Raise:

           CMError can be raised in-case of a failure.
        """
        raise cmerror.CMError('Not implemented')

    # pylint: disable=no-self-use, unused-argument
    def validate_set(self, props):
        """validate a configuration data addition/update

           Arguments:

           props: A dictionary of name-value pairs representing the changed
           properties.

           Raise:

           CMError can be raised if the change is not accepted by this plugin.
        """
        raise cmerror.CMError('Not implemented')

    # pylint: disable=no-self-use, unused-argument
    def validate_delete(self, props):
        """validate a configuration data delete

           Arguments:

           props: A list containing the names of deleted properties

           Raise:

           CMError can raised if the delete is not accepted by this plugin.
        """
        raise cmerror.CMError('Not implemented')

    def get_plugin_client(self):
        """get the plugin client object

           This API can be used by the plugin to get the client object which the
           plugin can use to access the configuration data. Notice that the data
           accessed by this is what is stored in the backend. The changed data
           is passed as argument to the different validate functions.

           Return:

           The plugin client object
        """
        return self.plugin_client
