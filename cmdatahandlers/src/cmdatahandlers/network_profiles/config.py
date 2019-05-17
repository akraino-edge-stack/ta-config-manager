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
        self.ROOT = 'cloud.network_profiles'
        self.DOMAIN = 'network_profiles'

    def init(self):
        pass

    def validate(self):
        self.validate_root()
        self._validate_network_profiles()

    def _validate_network_profiles(self):
        profiles = self.get_network_profiles()
        utils.validate_list_items_unique(profiles)
        for profile in profiles:
            self._validate_network_profile(profile)

    def _validate_network_profile(self, profile):
        bondinginterfaces = None
        try:
            bondinginterfaces = self.get_profile_bonding_interfaces(profile)
        except configerror.ConfigError:
            pass

        if bondinginterfaces:
            utils.validate_list_items_unique(bondinginterfaces)

            for bond in bondinginterfaces:
                bondedinterfaces = self.get_profile_bonded_interfaces(
                    profile, bond)
                utils.validate_list_items_unique(bondedinterfaces)
                if len(bondedinterfaces) < 2:
                    raise configerror.ConfigError(
                        'Number of bonded interfaces should be at least 2 in %s' % bond)

        mappedinterfaces = self.get_profile_network_mapped_interfaces(profile)

        utils.validate_list_items_unique(mappedinterfaces)

        netconf = self.confman.get_networking_config_handler()
        validnetworks = netconf.get_networks()
        for interface in mappedinterfaces:
            networks = self.get_profile_interface_mapped_networks(
                profile, interface)
            utils.validate_list_items_unique(networks)
            for network in networks:
                if network not in validnetworks:
                    raise configerror.ConfigError(
                        'Network %s is not valid' % network)

    def is_valid_profile(self, profile):
        """
        Check if given profile exists

        Arguments:
            The profile name

        Returns:
            True if given profile exists

        Raises:
            ConfigError in-case of an error
        """
        self.validate_root()
        profiles = self.get_network_profiles()
        if profile not in profiles:
            raise configerror.ConfigError('Invalid profile name %s' % profile)

    def get_network_profiles(self):
        """
        Get the network profiles list

        Returns:
            A list of network profile(s) names

        Raises:
            ConfigError in-case of an error
        """
        self.validate_root()
        return self.config[self.ROOT].keys()

    def get_profile_linux_bonding_options(self, profile):
        """
        Get the linux bonding options of a profile

        Arguments:
            The profile name

        Returns:
            The linux bonding options

        Raises:
            ConfigError in-case of an error
        """
        self.is_valid_profile(profile)

        if 'linux_bonding_options' not in self.config[self.ROOT][profile]:
            raise configerror.ConfigError(
                'profile %s has no linux bonding options' %
                profile)

        return self.config[self.ROOT][profile]['linux_bonding_options']

    def get_profile_bonding_interfaces(self, profile):
        """
        Get the bonding interfaces in a profile

        Arguments:
            The profile name

        Returns:
            A list of bonding interfaces names

        Raises:
            ConfigError in-case of an error
        """
        self.is_valid_profile(profile)

        if 'bonding_interfaces' not in self.config[self.ROOT][profile]:
            raise configerror.ConfigError(
                'Profile %s has no bonding interfaces' %
                profile)

        return self.config[self.ROOT][profile]['bonding_interfaces'].keys()

    def get_profile_bonded_interfaces(self, profile, bond):
        """
        Get the bonded interfaces in bond interface

        Arguments:
            The name of the profile
            The name of the bond interface

        Returns:
            A list of bonded interfaces names

        Raises:
            ConfigError in-case of an error
        """
        self.validate_root()
        bondinterfaces = self.get_profile_bonding_interfaces(profile)
        if bond not in bondinterfaces:
            raise configerror.ConfigError(
                'Invalid bond interface name %s in profile %s' %
                (bond, profile))

        return self.config[self.ROOT][profile]['bonding_interfaces'][bond]

    def get_profile_network_mapped_interfaces(self, profile):
        """
        Get the network mapped interfaces

        Arguments:
            The profile name

        Returns:
            A list of network mapped interfaces

        Raises:
            ConfigError in-case of an error
        """
        self.is_valid_profile(profile)

        if 'interface_net_mapping' not in self.config[self.ROOT][profile]:
            raise configerror.ConfigError(
                'Profile %s has now interface to network mapping' %
                profile)

        return self.config[self.ROOT][profile]['interface_net_mapping'].keys()

    def get_profile_interface_mapped_networks(self, profile, interface):
        """
        Get the networks mapped to a specific interface

        Arguments:
            The profile name
            The interface name

        Returns:
            A list of network names

        Raises:
            ConfigError in-case of an error
        """
        self.is_valid_profile(profile)
        mappedinterfaces = self.get_profile_network_mapped_interfaces(profile)
        if interface not in mappedinterfaces:
            raise configerror.ConfigError(
                'Interface %s is not valid for profile %s' %
                (interface, profile))

        return self.config[self.ROOT][profile]['interface_net_mapping'][interface]

    def get_profile_provider_network_interfaces(self, profile):
        """
        Get the list of provider network interfaces

        Arguments:
            The profile name

        Returns:
            A sorted list of network interface names

        Raises:
            ConfigError in-case of an error
        """
        self.is_valid_profile(profile)
        if 'provider_network_interfaces' not in self.config[self.ROOT][profile]:
            raise configerror.ConfigError(
                'Profile %s has no provider network interfaces' %
                profile)

        return sorted(self.config[self.ROOT][profile]
                      ['provider_network_interfaces'].keys())

    def _get_profile_provider_network_interface_dict(self, profile, interface):
        self.is_valid_profile(profile)
        interfaces = self.get_profile_provider_network_interfaces(profile)
        if interface not in interfaces:
            raise configerror.ConfigError(
                'Profile %s has no provider interface with name %s' %
                (profile, interface))

        return self.config[self.ROOT][profile]['provider_network_interfaces'][interface]

    def get_profile_provider_network_interface_type(self, profile, interface):
        """
        Get the type of a provider network interface

        Arguments:
            The profile name
            The interface name

        Returns:
            The type of the network interface

        Raises:
            ConfigError in-case of an error
        """
        iface_dict = self._get_profile_provider_network_interface_dict(
            profile, interface)
        if 'type' not in iface_dict:
            raise configerror.ConfigError(
                'Provider network interface %s in profile %s does not have a type!' %
                (interface, profile))

        return iface_dict['type']

    def is_provider_network_type_caas(self, profile, interface):
        """
        Is provider network type caas

        Arguments:
            The profile name
            The interface name

        Returns:
            True if provider network is for CaaS

        Raises:
            ConfigError in-case of an error
        """
        return self.get_profile_provider_network_interface_type(profile, interface) == 'caas'

    def get_profile_provider_interface_networks(self, profile, interface):
        """
        Get provider networks for the interface

        Arguments:
            The profile name
            The interface name

        Returns:
            A list of provider network names

        Raises:
            ConfigError in-case of an error
        """
        iface_dict = self._get_profile_provider_network_interface_dict(
            profile, interface)
        if 'provider_networks' not in iface_dict:
            raise configerror.ConfigError(
                'Profile %s has no provider networks for interface %s' %
                (profile, interface))

        return iface_dict['provider_networks']

    def get_profile_sriov_provider_networks(self, profile):
        """
        Get SR-IOV provider networks

        Arguments:
            The profile name

        Returns:
            A list of SR-IOV provider network names

        Raises:
            ConfigError in-case of an error
        """
        self.is_valid_profile(profile)
        if 'sriov_provider_networks' not in self.config[self.ROOT][profile]:
            raise configerror.ConfigError(
                'Profile %s has no SR-IOV provider networks' %
                profile)

        return self.config[self.ROOT][profile]['sriov_provider_networks'].keys()

    def get_profile_sriov_network_interfaces(self, profile, network):
        """
        Get SR-IOV provider network interfaces

        Arguments:
            The profile name
            The SR-IOV network name

        Returns:
            A list of SR-IOV provider network interface names

        Raises:
            ConfigError in-case of an error
        """
        if network not in self.get_profile_sriov_provider_networks(profile):
            raise configerror.ConfigError(
                'Profile %s has no SR-IOV provider network %s' %
                (profile, network))

        if 'interfaces' not in self.config[self.ROOT][profile]['sriov_provider_networks'][network]:
            raise configerror.ConfigError(
                'Profile %s has no SR-IOV provider network interfaces for the network %s' %
                (profile, network))

        return self.config[self.ROOT][profile]['sriov_provider_networks'][network]['interfaces']

    def is_sriov_network_trusted(self, profile, network):
        """
        Is SR-IOV provider network trusted (VF parameter)

        Arguments:
            The profile name
            The SR-IOV network name

        Returns:
            True if VFs should be configured as trusted in this network

        Raises:
            ConfigError in-case of an error
        """
        if network not in self.get_profile_sriov_provider_networks(profile):
            raise configerror.ConfigError(
                'Profile %s has no SR-IOV provider network %s' %
                (profile, network))

        return self.config[self.ROOT][profile]['sriov_provider_networks'][network].get('trusted') is True

    def is_sriov_network_type_caas(self, profile, network):
        """
        Is SR-IOV network type caas

        Arguments:
            The profile name
            The SR-IOV network name

        Returns:
            True if SR-IOV network is for CaaS

        Raises:
            ConfigError in-case of an error
        """
        if network not in self.get_profile_sriov_provider_networks(profile):
            raise configerror.ConfigError('Profile %s has no SR-IOV provider network %s' % (profile, network))

        return self.config[self.ROOT][profile]['sriov_provider_networks'][network].get('type') == 'caas'

    def get_profile(self, name):
        """
        Get the network profile data

        Arguments:
            The profile name

        Returns:
            A dict of network profile data

        """
        self.is_valid_profile(name)
        return self.config[self.ROOT][name]

    def dump(self):
        """ Dump all network profiles data. """

        self.validate_root()
        return self.config[self.ROOT]

    def add_profile(self, name, profile):
        """ Add network profile.

            Parameters
            ----------
            name : str, profile name.
            profile : dict, profile data

        """
        if name in self.config[self.ROOT]:
            raise configerror.ConfigError('Profile %s already exists' % name)

        data = {}
        data[name] = profile
        self.config[self.ROOT].update(data)

    def delete_profile(self, name):
        """ Delete network profile.

            Parameters
            ----------
            name : str, profile name.

        """
        self.is_valid_profile(name)
        self.config[self.ROOT].pop(name)
