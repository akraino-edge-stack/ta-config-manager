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
import logging
from cmframework.apis import cmerror


class CMBackendHandler(object):
    def __init__(self, plugin_path, **kw):
        try:
            logging.debug('Loading backend plugin from %s', plugin_path)
            # Separate class path and module name
            parts = plugin_path.rsplit('.', 1)
            self.plugin_path = parts[0]
            class_name = parts[1]
            logging.debug('Importing %s from %s', class_name, self.plugin_path)
            module = __import__(self.plugin_path, fromlist=[self.plugin_path])
            classobj = getattr(module, class_name)
            logging.debug('Constructing backend handler with args %r', kw)
            self.plugin = classobj(**kw)
        except ImportError as exp1:
            raise cmerror.CMError(str(exp1))
        except Exception as exp2:
            raise cmerror.CMError(str(exp2))

    def get_property(self, prop_name):
        logging.debug('get_property called for %s', prop_name)
        return self.plugin.get_property(prop_name)

    def get_properties(self, prop_filter):
        logging.debug('get_properties called with filter %s', prop_filter)
        return self.plugin.get_properties(prop_filter)

    def set_property(self, prop_name, prop_value):
        logging.debug('set_property called for setting %s=%s', prop_name, prop_value)
        return self.plugin.set_property(prop_name, prop_value)

    def set_properties(self, props):
        logging.debug('set_properties called for properties %s', str(props))
        return self.plugin.set_properties(props)

    def delete_property(self, prop_name):
        logging.debug('delete_property called for %s', prop_name)
        return self.plugin.delete_property(prop_name)

    def delete_properties(self, prop_filter):
        logging.debug('delete_properties called with filter %s', prop_filter)
        return self.plugin.delete_properties(prop_filter)
