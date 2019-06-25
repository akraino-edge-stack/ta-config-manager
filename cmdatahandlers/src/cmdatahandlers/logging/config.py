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
        self.ROOT = 'cloud'
        self.infra_log = 'infra_log_store'

    def init(self):
        pass

    def validate(self):
        self.validate_root()
        self._validate_infra_log_store()

    def _validate_infra_log_store(self):
        infra = self.get_infra_log_store()
        utils.validate_list_items_unique(infra)

    def get_infra_log_store(self):
        """
        Get the network profiles list

        Returns:
            A list of infra log store values

        Raises:
            ConfigError in-case of an error
        """
        self.validate_root()
        return self.config[self.ROOT].values()

    def set_infra_log_store(self, log_type='elasticsearch'):
        """
        Set set_infra_log_store

        Arguments:
            logging plugin type, which defaults to elasticsearch

        Raises:
            ConfigError in-case of an error
        """
        self.config[self.ROOT][self.infra_log] = log_type
