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

class Config(config.Config):
    def __init__(self, confman):
        super(Config, self).__init__(confman)
        self.ROOT = 'cloud.openstack'
        self.DOMAIN = 'openstack'

    def init(self):
        pass

    def _getopenstack(self):
        hostsconf = self.confman.get_hosts_config_handler()
        return hostsconf.get_service_profile_hosts('controller')

    def validate(self):
        if self._getopenstack():
            self.validate_root()
            self._validate_storage_backend()
            self.get_admin_password()

    def _validate_storage_backend(self):
        backend = self.get_storage_backend()
        storageconf = self.confman.get_storage_config_handler()
        backends = storageconf.get_storage_backends()
        if backend not in backends:
            raise configerror.ConfigError('Invalid storage backend %s' % backend)

    def get_admin_password(self):
        """ get the admin password

            Return:

            The admin password

            Raise:

            ConfigError in-case of an error
        """
        if not self._getopenstack():
            return ''

        self.validate_root()

        if 'admin_password' not in self.config[self.ROOT]:
            raise configerror.ConfigError('No admin_password specified')

        return self.config[self.ROOT]['admin_password']

    def get_storage_backend(self):
        """ get the openstack storage backend

            Return:

            The openstack storage backend name

            Raise:

            ConfigError in-case of an error
        """
        if not self._getopenstack():
            storageconf = self.confman.get_storage_config_handler()
            enabled_backends = storageconf.get_enabled_backends()
            if enabled_backends:
                return enabled_backends[0]
            return ''

        self.validate_root()

        if 'storage_backend'  not in self.config[self.ROOT]:
            raise configerror.ConfigError('No storage backend configured')

        return self.config[self.ROOT]['storage_backend']

    def get_instance_default_backend(self):
        """ get the openstack instance backend

            Return:

            The openstack instance backend name

            Raise:

            ConfigError in-case of an error
        """
        if not self._getopenstack():
            return "default"

        self.validate_root()

        if 'instance_default_backend' not in self.config[self.ROOT]:
            return "default"

        return self.config[self.ROOT]['instance_default_backend']

    def mask_sensitive_data(self):
        self.config[self.ROOT]['admin_password'] = self.MASK
