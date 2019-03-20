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
        self.ROOT='cloud.time'
        self.DOMAIN='time'

    def init(self):
        pass

    def validate(self):
        self.validate_root()

        if 'zone' not in self.config[self.ROOT]:
            raise configerror.ConfigError('No zone configuration found')

        if 'ntp_servers' not in self.config[self.ROOT]:
            raise configerror.ConfigError('No ntp servers found')

        if 'auth_type' not in self.config[self.ROOT]:
            self.config[self.ROOT]['auth_type'] = 'crypto'

        if 'serverkeys_path' not in self.config[self.ROOT]:
            self.config[self.ROOT]['serverkeys_path'] = ''

        self._validate_time_zone()
        self._validate_ntp_servers()

    def _validate_time_zone(self):
        import pytz
        try:
            zone = self.get_zone()
            pytz.timezone(zone)
        except:
            raise configerror.ConfigError('The timezone %s is not valid' % zone)

    def _validate_ntp_servers(self):
        servers = self.get_ntp_servers()
        utils.validate_list_items_unique(servers)

        for server in servers:
            utils.validate_ipv4_address(server)


    """ get the time zone

        Return:

        A string representing time zone

        Raise:

        ConfigError in-case of an error
    """
    def get_zone(self):
        self.validate_root()
        return self.config[self.ROOT]['zone']

    """ get the ntp servers

        Return:

        A list of ntp server addresses.

        Raise:

        ConfigError in-case of an error
    """
    def get_ntp_servers(self):
        self.validate_root()
        return self.config[self.ROOT]['ntp_servers']
    
    def get_auth_type(self):
        self.validate_root()
        return self.config[self.ROOT]['auth_type']

    def get_time_config(self):
        self.validate_root()
        return self.config[self.ROOT]

    def set_config(self, **args):
        if args['auth_type'] is not None:
            self.config[self.ROOT]['auth_type'] = args['auth_type']
        if args['servers'] is not None:
            self.config[self.ROOT]['ntp_servers'] = args['servers']
        if args['keyfile_url'] is not None:
            self.config[self.ROOT]['serverkeys_path'] = args['keyfile_url']
        if args['zone'] is not None:
            self.config[self.ROOT]['zone'] = args['zone']
        self.validate()
        return self.config[self.ROOT]
