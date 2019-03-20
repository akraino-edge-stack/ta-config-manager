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
from cmdatahandlers.api import config
from cmdatahandlers.api import utils

class Config(config.Config):

    def __init__(self, confman):
        super(Config, self).__init__(confman)
        self.ROOT = 'cloud.osoverrides'
        self.DOMAIN = 'osoverrides'

    def init(self):
        pass

    def validate(self):
        if self.ROOT not in self.config:
            return
        overrides = self.config[self.ROOT].get('osoverrides', {})
        if not isinstance(overrides, dict):
            raise configerror.ConfigError("OS overrides (osoverrides) must be defined as dictionary")
            

    def get_config_overrides(self):
        return self.config.get(self.ROOT, {}).get('osoverrides', {})
