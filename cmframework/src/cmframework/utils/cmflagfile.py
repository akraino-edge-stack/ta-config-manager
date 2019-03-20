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
import os.path
import os
import stat

from cmframework.apis import cmerror


class CMFlagFile(object):
    CM_FLAGFILE_DIR = '/mnt/config-manager'

    def __init__(self, name):
        logging.debug('CMFlagFile constructor called, name=%s', name)

        self._name = '{}/{}'.format(CMFlagFile.CM_FLAGFILE_DIR, name)

    def __nonzero__(self):
        return self.is_set()

    def is_set(self):
        logging.debug('is_set called')

        return os.path.exists(self._name)

    def set(self):
        logging.debug('set called')

        if not self.is_set():
            try:
                with open(self._name, 'w') as f:
                    os.chmod(self._name, stat.S_IRUSR | stat.S_IWUSR)
                    f.write('')
                    f.flush()
                    os.fsync(f.fileno())
            except IOError as exp:
                raise cmerror.CMError(str(exp))

    def unset(self):
        logging.debug('unset called')

        if self.is_set():
            try:
                os.remove(self._name)
            except IOError as exp:
                raise cmerror.CMError(str(exp))
