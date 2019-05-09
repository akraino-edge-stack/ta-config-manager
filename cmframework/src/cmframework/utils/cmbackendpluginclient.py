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
from cmframework.apis import cmpluginclient
from cmframework.utils import cmbackendhandler


class CMBackendPluginClient(cmpluginclient.CMPluginClient):
    def __init__(self, plugin_path, **args):
        self.backend = cmbackendhandler.CMBackendHandler(plugin_path, **args)

    def get_property(self, prop_name):
        return self.backend.get_property(prop_name)

    def get_properties(self, prop_filter):
        return self.backend.get_properties(prop_filter)

    def set_property(self, name, value):
        return self.backend.set_property(name, value)
