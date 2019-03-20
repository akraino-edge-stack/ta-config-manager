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

from cmframework.utils import cmpluginmanager
from cmframework.utils import cmpluginloader
from cmframework.utils import cmactivationwork

from cmframework.apis import cmactivator
from cmframework.server import cmactivatehandler


class CMActivateServerHandler(cmactivatehandler.CMActivateHandler,
                              cmpluginmanager.CMPluginManager,
                              cmpluginloader.CMPluginLoader.LoadingFilter):

    def __init__(self, plugins_path, plugin_client, changemonitor, activationstate_handler):
        cmpluginmanager.CMPluginManager.__init__(self, plugins_path)
        self.load_plugin()
        self.plugin_client = plugin_client
        self.changemonitor = changemonitor
        self.activationstate_handler = activationstate_handler

    def is_supported(self, activator_plugin):
        logging.debug('Checking %s', activator_plugin)
        return isinstance(activator_plugin, cmactivator.CMGlobalActivator)

    def load_plugin(self):
        plugin_filter = self
        pl = cmpluginloader.CMPluginLoader(self.plugins_path, plugin_filter)
        self.pluginlist, self.filterdict = pl.load()
        logging.info('pluginlist is %r', self.pluginlist)

    def activate_set(self, indata):
        return self._activate(indata, 'activate_set')

    def activate_delete(self, indata):
        return self._activate(indata, 'activate_delete')

    def activate_full(self, target_node, startup_activation=False):
        return self._activate(target_node, 'activate_full', startup_activation)

    def activate_node(self, target_node):
        return self._activate(target_node, 'activate_full')

    def _activate(self, indata, operation, startup_activation=False):
        logging.info('%s called with %s', operation, indata)
        failures = {}
        for plugin, objectname in self.pluginlist.iteritems():
            logging.info('Running plugin %s.%s', plugin, operation)
            func = None
            try:
                class_name = getattr(objectname, plugin)
                instance = class_name()
                instance.plugin_client = self.plugin_client
                func = getattr(instance, operation)
                if operation != 'activate_full':
                    filtername = self.filterdict[plugin]
                    inputdata = self.build_input(indata, filtername)

                    if not inputdata:
                        logging.info('Skipping plugin %s as no input data is to be processed by it',
                                     plugin)
                        continue

                    start_time = time.time()
                    func(inputdata)
                    logging.info('Plugin %s.%s took %s seconds', plugin, operation,
                                 time.time() - start_time)
                else:
                    if startup_activation:
                        if plugin not in self.activationstate_handler.get_full_failed():
                            logging.info('Skipping plugin %s during startup as '
                                         'it has not failed in last activation', plugin)
                            continue

                    start_time = time.time()
                    func(indata)
                    logging.info('Plugin %s.%s took %s seconds', plugin, operation,
                                 time.time() - start_time)
            except AttributeError as exp:
                logging.info('Plugin %s does not have %s defined', plugin, operation)
                logging.info(str(exp))
                failures[str(plugin)] = 'Plugin does not have {} defined'.format(operation)
                continue
            except Exception as exp:  # pylint: disable=broad-except
                failures[str(plugin)] = str(exp)
                logging.error('Skipping %s, got exception %s', plugin, str(exp))
                failures[str(plugin)] = str(exp)
                continue

        logging.info('%s done with %s', operation, indata)

        return failures

    def activate(self, work):
        logging.debug('CMAcivateServerHandler activating %s', work)
        failures = {}
        if work.get_operation() == cmactivationwork.CMActivationWork.OPER_SET:
            failures = self.activate_set(work.get_props())
        elif work.get_operation() == cmactivationwork.CMActivationWork.OPER_DELETE:
            failures = self.activate_delete(work.get_props())
        elif work.get_operation() == cmactivationwork.CMActivationWork.OPER_FULL:
            startup_activation = work.is_startup_activation()
            failures = self.activate_full(work.get_target(), startup_activation)
        elif work.get_operation() == cmactivationwork.CMActivationWork.OPER_NODE:
            failures = self.activate_node(work.get_target())
        else:
            logging.error('Unsupported activation operation %s', work.get_operation())

        if work.uuid_value:
            if failures:
                self.changemonitor.change_nok(work.uuid_value, failures)
            else:
                self.changemonitor.change_ok(work.uuid_value)

        return failures
