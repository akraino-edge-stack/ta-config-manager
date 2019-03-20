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
# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
import logging

from cmframework.utils.cmpluginloader import CMPluginLoader
from cmframework.utils.cmpluginmanager import CMPluginManager


class CMValidator(CMPluginManager):
    def __init__(self, plugins_path, plugin_client):
        logging.info('Validator constructor, plugins_path is %s', plugins_path)
        CMPluginManager.__init__(self, plugins_path)
        self.load_plugin()
        self.plugin_client = plugin_client

    def load_plugin(self):
        pl = CMPluginLoader(self.plugins_path)
        self.pluginlist, self.filterdict = pl.load()
        logging.info('Plugin(s): %r', self.pluginlist)
        logging.info('Subscription(s): %r', self.filterdict)

    def validate_delete(self, indata):
        self.validate_plugins(indata, 'validate_delete')

    def validate_set(self, indata):
        self.validate_plugins(indata, 'validate_set')

    def validate_plugins(self, indata, operation):
        # import pdb; pdb.set_trace()
        logging.debug('validate_plugins called with data %s', indata)
        for plugin, objectname in self.pluginlist.iteritems():
            filtername = self.filterdict[plugin]
            inputdata = self.build_input(indata, filtername)
            if inputdata:
                logging.debug('Calling validation plugin %s with %s', plugin, inputdata)
                class_name = getattr(objectname, plugin)
                instance = class_name()
                instance.plugin_client = self.plugin_client
                try:
                    func = getattr(instance, operation)
                    func(inputdata)
                except AttributeError:
                    logging.info('Plugin %s does have function %s implemented', plugin, operation)
