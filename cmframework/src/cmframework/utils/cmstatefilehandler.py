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
from urlparse import urlparse
from configparser import ConfigParser
import os.path
import os
import stat

from cmframework.apis import cmerror
from cmframework.apis import cmstate


class CMStateFileHandler(cmstate.CMState):
    def __init__(self, **kw):
        uridata = urlparse(kw['uri'])
        self.path = uridata.path
        self.configparser = ConfigParser()
        self._load_config_file()

    def _load_config_file(self):
        try:
            if os.path.isfile(self.path):
                with open(self.path, 'r') as cf:
                    self.configparser.read_file(cf)
            else:
                with open(self.path, 'w') as cf:
                    pass
        except IOError as ex:
            raise cmerror.CMError(str(ex))

    def _write_config_file(self):
        try:
            with open(self.path, 'w') as cf:
                os.chmod(self.path, stat.S_IRUSR | stat.S_IWUSR)
                self.configparser.write(cf)
        except IOError as ex:
            raise cmerror.CMError(str(ex))

    def get(self, domain, name):
        logging.debug('get called for %s %s', domain, name)

        if self.configparser.has_section(domain):
            if self.configparser.has_option(domain, name):
                return self.configparser.get(domain, name)

        return None

    def get_domain(self, domain):
        logging.debug('get_domain called for %s', domain)

        if self.configparser.has_section(domain):
            return self.configparser.items(domain)

        return None

    def set(self, domain, name, value):
        logging.debug('set called for setting %s %s=%s', domain, name, value)

        if not self.configparser.has_section(domain):
            self.configparser.add_section(domain)

        self.configparser.set(domain, name, value)

        self._write_config_file()

    def get_domains(self):
        logging.debug('get_domains called')

        return self.configparser.sections()

    def delete(self, domain, name):
        logging.debug('delete called for %s %s', domain, name)

        if self.configparser.has_section(domain):
            self.configparser.remove_option(domain, name)

        self._write_config_file()

    def delete_domain(self, domain):
        logging.debug('delete_domain called for %s', domain)

        self.configparser.remove_section(domain)

        self._write_config_file()
