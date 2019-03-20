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

import logging
import time

from cmframework.apis.cmerror import CMError
from cmframework.apis.cmmanage import CMManage
from cmframework.utils.cmpluginloader import CMPluginLoader
from cmframework.utils.cmdependencysort import CMDependencySort

from cmdatahandlers.api.configmanager import ConfigManager
from cmdatahandlers.api import utils


class CMUpdateImpl(object):
    def __init__(self, plugins_path, server_ip='config-manager', server_port=61100,
                 client_lib_impl_module='cmframework.lib.CMClientImpl', verbose_logger=None):
        logging.info('CMUpdateImpl constructor, plugins_path is %s', plugins_path)

        self._plugins_path = plugins_path
        self._handlers = {}
        self._sorted_handlers = []

        self._load_handlers()
        self._load_dependencies()

        self.uuid_value = None

        self.api = CMManage(server_ip, server_port, client_lib_impl_module, verbose_logger)

    def _load_handlers(self):
        loader = CMPluginLoader(self._plugins_path)
        handler_modules, _ = loader.load()
        logging.info('Handler module(s): %r', handler_modules)

        for handler_class_name, module in handler_modules.iteritems():
            handler_class = getattr(module, handler_class_name)
            handler = handler_class()
            self._handlers[handler_class_name] = handler

    def update(self, confman=None):
        logging.info('Taking snapshot of the original configuration just in-case')
        now = int(round(time.time()*1000))
        snapshot_name = 'cmupdate-' + str(now)
        self.api.create_snapshot(snapshot_name)
        if not confman:
            properties = self.api.get_properties('.*')
            propsjson = utils.unflatten_config_data(properties)
            confman = ConfigManager(propsjson)

        for handler in self._sorted_handlers:
            try:
                logging.debug('Calling update for %s', handler)
                self._handlers[handler].update(confman)
                logging.debug('update for %s done', handler)
            except Exception as ex:  # pylint: disable=broad-except
                logging.warning('Update handler %s failed: %s', handler, str(ex))
                raise

        properties = confman.get_config()
        flatprops = utils.flatten_config_data(properties)

        try:
            self.uuid_value = self.api.set_properties(flatprops, True)
        except Exception as exp:  # pylint: disable=broad-except
            for handler in self._sorted_handlers:
                try:
                    logging.debug('Calling validation_failed for %s', handler)
                    self._handlers[handler].validation_failed(confman)
                except Exception as ex2:  # pylint: disable=broad-except
                    logging.warning('Update handler %s validation_failed raised exception: %s',
                                    handler, str(ex2))
            raise exp

    def wait_activation(self):
        if self.uuid_value:
            self.api.wait_activation(self.uuid_value)

    @staticmethod
    def _read_dependency_file(file_name):
        before_list = []
        after_list = []

        try:
            with open(file_name, 'r') as deps_file:
                while True:
                    line = deps_file.readline()
                    if not line:
                        break
                    if line.startswith('Before:'):
                        before_list = line[7:].strip().replace(' ', '').split(',')
                    if line.startswith('After:'):
                        after_list = line[6:].strip().replace(' ', '').split(',')
        except IOError:
            logging.debug('Dependency file %s not found.', file_name)

        return (before_list, after_list)

    def _load_dependencies(self):
        before_graph = {}
        after_graph = {}

        for handler in self._handlers.values():
            deps_filename = '{}/{}.deps'.format(self._plugins_path, handler)
            before_list, after_list = self._read_dependency_file(deps_filename)

            for before_dep in before_list:
                if not self._handlers.get(before_dep, None):
                    raise CMError(
                        'Unexisting handler {} referred in handler {}\'s "Before" dependencies'
                        .format(before_dep, handler))
            for after_dep in after_list:
                if not self._handlers.get(after_dep, None):
                    raise CMError(
                        'Unexisting handler {} referred in handler {}\'s "After" dependencies'
                        .format(after_dep, handler))

            before_graph[str(handler)] = before_list
            after_graph[str(handler)] = after_list

        sorter = CMDependencySort(after_graph, before_graph)
        self._sorted_handlers = sorter.sort()
