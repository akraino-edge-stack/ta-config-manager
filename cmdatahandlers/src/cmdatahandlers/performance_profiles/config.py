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

    DEFAULT_HUGEPAGESZ = 'default_hugepagesz'
    HUGEPAGESZ = 'hugepagesz'
    HUGEPAGES = 'hugepages'
    PLATFORM_CPUS = 'platform_cpus'
    OVS_DPDK_CPUS = 'ovs_dpdk_cpus'
    PROFILE_OPTIONS = {DEFAULT_HUGEPAGESZ: 'get_profile_default_hugepage_size',
                       HUGEPAGESZ: 'get_profile_hugepage_size',
                       HUGEPAGES: 'get_profile_hugepage_count',
                       PLATFORM_CPUS: 'get_platform_cpus',
                       OVS_DPDK_CPUS: 'get_ovs_dpdk_cpus'}

    ERR_INVALID_PROFILE = 'Invalid profile name {}'
    ERR_MISSING_PROFILE_KEY = 'Profile {} does not have %s'
    ERR_MISSING_DEFAULT_HUGEPAGESZ = ERR_MISSING_PROFILE_KEY % DEFAULT_HUGEPAGESZ
    ERR_MISSING_HUGEPAGESZ = ERR_MISSING_PROFILE_KEY % HUGEPAGESZ
    ERR_MISSING_HUGEPAGES = ERR_MISSING_PROFILE_KEY % HUGEPAGES
    ERR_MISSING_PLATFORM_CPUS = ERR_MISSING_PROFILE_KEY % PLATFORM_CPUS
    ERR_MISSING_OVS_DPDK_CPUS = ERR_MISSING_PROFILE_KEY % OVS_DPDK_CPUS

    @staticmethod
    def raise_error(context, err_type):
        raise configerror.ConfigError(err_type.format(context))

    def __init__(self, confman):
        super(Config, self).__init__(confman)
        self.ROOT = 'cloud.performance_profiles'
        self.DOMAIN = 'performance_profiles'

    def init(self):
        pass

    def validate(self):
        self.validate_root()
        self._validate_performance_profiles()

    def _validate_performance_profiles(self):
        profiles = self.get_performance_profiles()
        utils.validate_list_items_unique(profiles)
        for profile in profiles:
            self._validate_performance_profile(profile)

    def _validate_performance_profile(self, profile):
        self.get_profile_default_hugepage_size(profile)
        self.get_profile_hugepage_size(profile)
        self.get_profile_hugepage_count(profile)
        self.get_platform_cpus(profile)
        self.get_ovs_dpdk_cpus(profile)

    def is_valid_profile(self, profile):
        profiles = self.get_performance_profiles()
        if profile not in profiles:
            self.raise_error(profile, self.ERR_INVALID_PROFILE)

    def get_performance_profiles(self):
        """ get the performance profiles list

            Return:

            A list of performance profile(s) names

            Raise:

            ConfigError in-case of an error
        """
        self.validate_root()
        return self.config[self.ROOT].keys()

    # pylint: disable=invalid-name
    def get_profile_default_hugepage_size(self, profile):
        """ get the default hugepage size

            Argument:

            profile name

            Return:

            The default hugepage size

            Raise:

            ConfigError in-case of an error
        """
        self.is_valid_profile(profile)

        if self.DEFAULT_HUGEPAGESZ not in self.config[self.ROOT][profile]:
            self.raise_error(profile, self.ERR_MISSING_DEFAULT_HUGEPAGESZ)

        return self.config[self.ROOT][profile][self.DEFAULT_HUGEPAGESZ]

    def get_profile_hugepage_size(self, profile):
        """ get the hugepage size

            Argument:

            profile name

            Return:

            The hugepage size

            Raise:

            ConfigError in-case of an error
        """
        self.is_valid_profile(profile)

        if self.HUGEPAGESZ not in self.config[self.ROOT][profile]:
            self.raise_error(profile, self.ERR_MISSING_HUGEPAGESZ)

        return self.config[self.ROOT][profile][self.HUGEPAGESZ]

    def get_profile_hugepage_count(self, profile):
        """ get the hugepage count

            Argument:

            profile name

            Return:

            The hugepage count

            Raise:

            ConfigError in-case of an error
        """
        self.is_valid_profile(profile)

        if self.HUGEPAGES not in self.config[self.ROOT][profile]:
            self.raise_error(profile, self.ERR_MISSING_HUGEPAGES)

        return self.config[self.ROOT][profile][self.HUGEPAGES]

    def get_platform_cpus(self, profile):
        """ get the Platforma CPUs (isolate CPUs from the general scheduler).

            Argument:

            profile name

            Return:

            The platform CPUs dictionary

            Raise:

            ConfigError in-case of an error
        """
        self.is_valid_profile(profile)

        if self.PLATFORM_CPUS not in self.config[self.ROOT][profile]:
            self.raise_error(profile, self.ERR_MISSING_PLATFORM_CPUS)

        return self.config[self.ROOT][profile][self.PLATFORM_CPUS]

    def get_ovs_dpdk_cpus(self, profile):
        """ get the ovs-dpdk cpu(s)

            Argument:

            profile name

            Return:

            The ovs-dpdk dedicated cpu(s) string

            Raise:

            ConfigError in-case of an error
        """
        self.is_valid_profile(profile)

        if self.OVS_DPDK_CPUS not in self.config[self.ROOT][profile]:
            self.raise_error(profile, self.ERR_MISSING_OVS_DPDK_CPUS)

        return self.config[self.ROOT][profile][self.OVS_DPDK_CPUS]

    def dump(self):
        """ Dump all performaceprofiles data. """

        self.validate_root()
        return self.config[self.ROOT]

    def _fill_option_value(self, profile_data, profile, option, value):
        if value is None:
            try:
                value = getattr(self, self.PROFILE_OPTIONS[option])(profile)
            except configerror.ConfigError:
                return
        profile_data.update({option:value})

    # pylint: disable=too-many-arguments
    def update(self, name, platform_cpus=None, ovs_dpdk_cpus=None, hugepages=None,
               default_hugepagesz=None, hugepagesz=None):
        """ Update performance profile, overwriting existing profile.

            Parameters
            ----------
            name : str
                   profile name.
            platform_cpus : dict, optional
                       Platform CPUs.
                       The syntax is: {'numa0': <int>, 'numa1': <int>, ..., 'numaN': <int>}
            ovs_dpdk_cpus : dict, optional
                        OVS-DPDK dedicated cores.
                        The syntax is the same as platform_cpus.
            hugepages : int, optional
                        The number of allocated persistent huge pages.
            default_hugepagesz : str, optional
                                 Default huge page size (the default value is '1G').
                                 Valid values are '2M' and '1G'
            hugepagesz : str, optional
                         Huge page size (the default value is '1G').
                         Valid values are '2M' and '1G'

        """
        data = {}
        self._fill_option_value(data, name, 'platform_cpus', platform_cpus)
        self._fill_option_value(data, name, 'ovs_dpdk_cpus', ovs_dpdk_cpus)
        self._fill_option_value(data, name, 'hugepages', hugepages)
        self._fill_option_value(data, name, 'default_hugepagesz', default_hugepagesz)
        self._fill_option_value(data, name, 'hugepagesz', hugepagesz)
        self.config[self.ROOT].update({name:data})

    def delete(self, name):
        """ Remove profile.

            Parametes
            ---------
            name : str
                   profile name.

            Raises
            ------
            Raises ConfigError if profile does not exist.
        """
        try:
            self.config[self.ROOT].pop(name)
        except KeyError:
            self.raise_error(name, self.ERR_INVALID_PROFILE)