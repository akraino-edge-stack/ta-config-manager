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
        self.ROOT = 'cloud.users'
        self.DOMAIN = 'users'

    def init(self):
        pass

    def validate(self):
        self.validate_root()

    def get_users(self):
        """ get the users list

            Return:

            A list of users

            Raise:

            ConfigError in-case of an error
        """
        self.validate_root()
        return []

    def get_user_password(self, user):
        """ get the password for a user

            Return:

            A string representing the password

            Raise:

            ConfigError in-case of an error
        """
        raise configerror.ConfigError('Invalid user %s' % user)

    def get_admin_user_password(self):
        """ get the admin user password

            Return:

            A string representing the admin user password

            Raise:

            ConfigError in-case of an error
        """
        return self.config[self.ROOT]['admin_user_password']

    def get_admin_user(self):
        """ get the admin user

            Return:

            A string representing the admin user

            Raise:

            ConfigError in-case of an error
        """
        return self.config[self.ROOT]['admin_user_name']

    def get_initial_user_name(self):
        """ get the initial user name

            Return:

            A string representing the initial user name

            Raise:

            ConfigError in-case of an error
        """
        return self.config[self.ROOT]['initial_user_name']

    def get_initial_user_password(self):
        """ get the initial user password

            Return:

            A string representing the initial user password

            Raise:

            ConfigError in-case of an error
        """
        return self.config[self.ROOT]['initial_user_password']

    def mask_sensitive_data(self):
        self.config[self.ROOT]['admin_user_password'] = self.MASK
        self.config[self.ROOT]['initial_user_password'] = self.MASK

    def get_admin_password(self):
        """ get the admin password

            Return:

            The admin password

            Raise:

            ConfigError in-case of an error
        """
        return self.config[self.ROOT]['admin_password']

