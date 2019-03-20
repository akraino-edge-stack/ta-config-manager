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
import os
import imp
import sys
import logging

from cmframework.apis import cmerror


class CMPluginLoader(object):
    class LoadingFilter(object):
        # pylint: disable=no-self-use, unused-argument
        def is_supported(self, plugin):
            return True

    def __init__(self, plugin_location, plugin_filter=None):
        self.location = plugin_location
        sys.path.append(self.location)
        self.pluginslist = []
        self.loaded_plugin = {}
        self.filterlist = {}
        self.plugin_filter = plugin_filter

    def find_plugin(self):
        logging.debug('finding plugins in %s', self.location)
        listofplugin = os.listdir(self.location)
        for plugin in listofplugin:
            if plugin.endswith('.py'):
                logging.debug('Adding plugin %s', plugin)
                self.pluginslist.append(plugin.replace(".py", ""))

    def sort_plugin(self):
        logging.debug('Sorting plugins')
        self.pluginslist.sort()

    def load_plugin(self):
        for plugin in self.pluginslist:
            logging.debug('Loading plugin %s', plugin)
            fp, pathname, description = imp.find_module(plugin)
            try:
                pluginmodule = imp.load_module(plugin, fp, pathname, description)
                add_plugin = True
                if self.plugin_filter:
                    class_name = getattr(pluginmodule, plugin)
                    instance = class_name()
                    add_plugin = self.plugin_filter.is_supported(instance)
                if add_plugin:
                    logging.info('Adding plugin %s to list', plugin)
                    self.loaded_plugin[plugin] = pluginmodule
                else:
                    logging.info(
                        'Skipping plugin %s as it does not match configured filter', plugin)
            except Exception as exp:  # pylint: disable=broad-except
                logging.error('Failed to load plugin %s, got exp %s', plugin, str(exp))
                raise cmerror.CMError('Loading %s plugin failed' % plugin)
            finally:
                if fp:
                    fp.close()

    def build_filter_dict(self):
        faulty_plugins = []
        for plugin, objectname in self.loaded_plugin.iteritems():
            logging.debug('Getting the subsription info from %s %s', plugin, objectname)
            try:
                class_name = getattr(objectname, plugin)
                instance = class_name()
                filtername = instance.get_subscription_info()
                self.filterlist[plugin] = filtername
            except Exception as exp:  # pylint: disable=broad-except
                logging.error('Getting subscription failed for %s %s, got exp %s',
                              plugin, objectname, str(exp))
                faulty_plugins.append(plugin)

        for plugin in faulty_plugins:
            del self.loaded_plugin[plugin]

    # pylint: disable=no-self-use
    def validate_plugin(self):
        pass

    def load(self):
        self.find_plugin()
        self.sort_plugin()
        self.load_plugin()
        self.build_filter_dict()
        return self.loaded_plugin, self.filterlist


def main():
    pl = CMPluginLoader("plug_in/tst")
    a, b = pl.load()
    print a
    print b


if __name__ == '__main__':
    main()
