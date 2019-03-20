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


class CMStateHandler(object):
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
            logging.debug('Constructing state handler with args %r', kw)
            self.plugin = classobj(**kw)
        except ImportError as exp1:
            raise cmerror.CMError(str(exp1))
        except Exception as exp2:
            raise cmerror.CMError(str(exp2))

    def get(self, domain, name):
        logging.debug('get called for %s %s', domain, name)
        return self.plugin.get(domain, name)

    def get_domain(self, domain):
        logging.debug('get_domain called for %s', domain)
        return self.plugin.get_domain(domain)

    def set(self, domain, name, value):
        logging.debug('set called for setting %s %s=%s', domain, name, value)
        return self.plugin.set(domain, name, value)

    def get_domains(self):
        logging.debug('get_domains called')
        return self.plugin.get_domains()

    def delete(self, domain, name):
        logging.debug('delete called for %s %s', domain, name)
        return self.plugin.delete(domain, name)

    def delete_domain(self, domain):
        logging.debug('delete_domain called for %s', domain)
        return self.plugin.delete_domain(domain)
