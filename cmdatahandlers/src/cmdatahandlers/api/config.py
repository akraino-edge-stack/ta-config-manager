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

from cmdatahandlers.api import configerror

class Config(object):
    def __init__(self, confman):
        self.confman = confman
        self.config = confman.get_config()
        self.DOMAIN = None
        self.ROOT = None
        self.MASK = '*******'

    def init(self):
        raise configerror.ConfigError('Not implemented')

    def validate_root(self):
        if self.ROOT not in self.config:
            raise configerror.ConfigError('No %s configuration found' % self.DOMAIN)

    def get_domain(self):
        return self.DOMAIN

    def validate(self):
        raise configerror.ConfigError('Not implemented')

    def mask_sensitive_data(self):
        pass
