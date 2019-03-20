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
from __future__ import print_function
import json
import yaml

from cmframework.apis import cmerror
from cmframework.utils.cmpluginloader import CMPluginLoader
from cmdatahandlers.api import configmanager


class UserConfig(object):

    def __init__(self, user_config_file, plugin_path):
        self.user_config_file = user_config_file
        self.removed_values = ['version']
        self.pluginloader = UserConfigPluginLoader(plugin_path)

    def get_flat_config(self):
        try:
            result = {}
            stream = file(self.user_config_file, 'r')
            tmp = yaml.load(stream)
            userconfig = {}
            for key in tmp.keys():
                userconfig['cloud.' + key] = tmp[key]

            confman = configmanager.ConfigManager(userconfig)
            self.pluginloader.load()
            plugins = self.pluginloader.get_plugin_instances()
            for _, plugin in plugins.iteritems():
                plugin.handle(confman)

            # change the multi-level deictionary to one level dictionary mapping
            # the key to a josn string representation of the value.
            for key, value in userconfig.iteritems():
                result[key] = json.dumps(value)

            return result
        except Exception as exp:
            raise cmerror.CMError("Failed to load user config %(userconfig)s: %(failure)s" %
                                  {'userconfig': self.user_config_file,
                                   'failure': str(exp)})


class UserConfigPluginLoader(CMPluginLoader):
    def __init__(self, plugin_location, plugin_filter=None):
        super(UserConfigPluginLoader, self).__init__(plugin_location, plugin_filter)

    def build_filter_dict(self):
        pass

    def get_plugin_instances(self):
        plugs = {}
        for plugin, module in self.loaded_plugin.iteritems():
            class_name = getattr(module, plugin)
            instance = class_name()
            plugs[plugin] = instance
        return plugs


def main():
    import argparse
    import sys
    import traceback

    parser = argparse.ArgumentParser(description='Test userconfig handler', prog=sys.argv[0])

    parser.add_argument('--config',
                        required=True,
                        dest='config',
                        metavar='CONFIG',
                        help='The user config yaml file',
                        type=str,
                        action='store')

    parser.add_argument('--plugins',
                        required=True,
                        dest='plugins',
                        metavar='PLUGINS',
                        help='The path to userconfig plugin(s)',
                        type=str,
                        action='store')

    try:
        args = parser.parse_args(sys.argv[1:])
        config = UserConfig(args.config, args.plugins)
        data = config.get_flat_config()
        for key, value in data.iteritems():
            print('%s=%s' % (key, value))

    except Exception as exp:  # pylint: disable=broad-except
        print("Got exp: %s" % exp)
        traceback.print_exc()
        sys.exit(1)
    sys.exit(1)


if __name__ == '__main__':
    main()
