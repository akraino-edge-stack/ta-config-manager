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


class CMUserConfigPlugin(object):

    def __init__(self):
        pass

    # pylint: disable=no-self-use,unused-argument
    def handle(self, confman):
        """provide configuration to CM by interpreting user config

           Arguments:

           confman: The configuration manager object used to manipulate the
           configuration data.

           Raise:

           CMError is raised in-case of failure
        """

        raise cmerror.CMError('No implemented')
