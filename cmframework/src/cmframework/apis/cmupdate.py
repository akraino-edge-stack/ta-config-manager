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

from cmframework.lib.cmupdateimpl import CMUpdateImpl


class CMUpdate(object):
    def __init__(self, plugins_path, server_ip='config-manager', server_port=61100,
                 client_lib_impl_module='cmframework.lib.CMClientImpl', verbose_logger=None):
        logging.info('CMUpdate constructor, plugins_path is %s', plugins_path)

        self._update_lib = CMUpdateImpl(plugins_path,
                                        server_ip,
                                        server_port,
                                        client_lib_impl_module,
                                        verbose_logger)

    def update(self, confman=None):
        self._update_lib.update(confman)

    def wait_activation(self):
        self._update_lib.wait_activation()
