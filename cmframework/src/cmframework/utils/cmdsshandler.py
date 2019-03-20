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

from cmframework.apis import cmerror
from cmframework.apis import cmstate
from dss.client import dss_client
from dss.api import dss_error


class CMDSSHandler(cmstate.CMState):
    def __init__(self, **kw):
        uridata = urlparse(kw['uri'])
        socket = uridata.path
        self.client = dss_client.Client(socket)

    def _domain_exists(self, domain):
        return domain in self.get_domains()

    def _name_exists_in_domain(self, domain, name):
        return name in self.get_domain(domain)

    def get(self, domain, name):
        logging.debug('get called for %s %s', domain, name)

        if self._domain_exists(domain):
            try:
                domain_data = self.client.get_domain(domain)
                return domain_data.get(name, None)
            except dss_error.Error as ex:
                raise cmerror.CMError(str(ex))

        return None

    def get_domain(self, domain):
        logging.debug('get_domain called for %s', domain)

        if self._domain_exists(domain):
            try:
                return self.client.get_domain(domain)
            except dss_error.Error as ex:
                raise cmerror.CMError(str(ex))

        return None

    def set(self, domain, name, value):
        logging.debug('set called for setting %s %s=%s', domain, name, value)
        try:
            return self.client.set(domain, name, value)
        except dss_error.Error as ex:
            raise cmerror.CMError(str(ex))

    def get_domains(self):
        logging.debug('get_domains called')
        try:
            return self.client.get_domains()
        except dss_error.Error as ex:
            raise cmerror.CMError(str(ex))

    def delete(self, domain, name):
        logging.debug('delete called for %s %s', domain, name)

        if self._domain_exists(domain):
            if self._name_exists_in_domain(domain, name):
                try:
                    self.client.delete(domain, name)
                except dss_error.Error as ex:
                    raise cmerror.CMError(str(ex))

    def delete_domain(self, domain):
        logging.debug('delete_domain called for %s', domain)

        if self._domain_exists(domain):
            try:
                self.client.delete_domain(domain)
            except dss_error.Error as ex:
                raise cmerror.CMError(str(ex))
