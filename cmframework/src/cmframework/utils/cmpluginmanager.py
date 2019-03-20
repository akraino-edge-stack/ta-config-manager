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
import re
import logging

from cmframework.apis import cmerror


class CMPluginManager(object):

    def __init__(self, plugins_path):
        self.pluginlist = {}
        self.filterdict = {}
        self.plugins_path = plugins_path

    # pylint: disable=no-self-use
    def load_plugin(self):
        raise cmerror.CMError('Not implemented')

    # pylint: disable=no-self-use
    def build_input(self, indata, filtername):
        search_re = re.compile(filtername)
        if isinstance(indata, dict):
            filter_data = {}
            for key, value in indata.iteritems():
                logging.debug('Matching %s against %s', key, filtername)
                if search_re.match(key):
                    filter_data[key] = value
        else:
            filter_data = []
            for key in indata:
                logging.debug('Matching %s against %s', key, filtername)
                if search_re.match(key):
                    filter_data.append(key)

        return filter_data
