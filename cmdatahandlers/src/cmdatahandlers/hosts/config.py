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

import re

from cmdatahandlers.api import configerror
from cmdatahandlers.api import config
from cmdatahandlers.api import utils
from serviceprofiles import profiles

VNF_EMBEDDED_RESERVED_MEMORY = "512Mi"
DUAL_VIM_CONTROLLER_RESERVED_MEMORY = "64Gi"
DUAL_VIM_DEFAULT_RESERVED_MEMORY = "32Gi"
MIDDLEWARE_RESERVED_MEMORY = "12Gi"

class Config(config.Config):
    def __init__(self, confman):
        super(Config, self).__init__(confman)
        self.ROOT = 'cloud.hosts'
        self.DOMAIN = 'hosts'
        try:
            self.update_service_profiles()
        except Exception:
            pass

    def init(self):
        pass

    def validate(self):
        hosts = []
        try:
            hosts = self.get_hosts()
        except configerror.ConfigError:
            pass

        if hosts:
            utils.validate_list_items_unique(hosts)

        for host in hosts:
            self._validate_host(host)

    def mask_sensitive_data(self):
        for hostname in self.config[self.ROOT].keys():
            self.config[self.ROOT][hostname]['hwmgmt']['password'] = self.MASK
            self.config[self.ROOT][hostname]['hwmgmt']['snmpv2_trap_community_string'] = self.MASK
            self.config[self.ROOT][hostname]['hwmgmt']['snmpv3_authpass'] = self.MASK
            self.config[self.ROOT][hostname]['hwmgmt']['snmpv3_privpass'] = self.MASK

    def _validate_host(self, hostname):
        self._validate_hwmgmt(hostname)
        self._validate_service_profiles(hostname)
        self._validate_network_profiles(hostname)
        self._validate_performance_profiles(hostname)
        self._validate_storage_profiles(hostname)

    def _validate_hwmgmt(self, hostname):
        ip = self.get_hwmgmt_ip(hostname)
        utils.validate_ipv4_address(ip)
        self.get_hwmgmt_user(hostname)
        self.get_hwmgmt_password(hostname)
        netconf = self.confman.get_networking_config_handler()

        hwmgmtnet = None
        try:
            hwmgmtnet = netconf.get_hwmgmt_network_name()
        except configerror.ConfigError:
            pass

        if hwmgmtnet:
            domain = self.get_host_network_domain(hostname)
            cidr = netconf.get_network_cidr(hwmgmtnet, domain)
            utils.validate_ip_in_network(ip, cidr)

    def get_hwmgmt_priv_level(self, hostname):
        """get the hwmgmt IPMI privilege level.  Defaults to ADMINISTRATOR

           Arguments:

           hostname: The name of the node

           Return:

           The prvilege level, or ADMINISTRATOR if unspecified

           Raise:

           ConfigError in-case of an error
        """
        self._validate_hostname(hostname)

        if 'hwmgmt' not in self.config[self.ROOT][hostname]:
            raise configerror.ConfigError('No hwmgmt info defined for host')

        return self.config[self.ROOT][hostname]['hwmgmt'].get('priv_level', 'ADMINISTRATOR')

    def _validate_service_profiles(self, hostname):
        node_profiles = self.get_service_profiles(hostname)
        utils.validate_list_items_unique(node_profiles)
        service_profiles_lib = profiles.Profiles()
        serviceprofiles = service_profiles_lib.get_service_profiles()
        for profile in node_profiles:
            if profile not in serviceprofiles:
                raise configerror.ConfigError('Invalid service profile %s specified for host %s' % (profile, hostname))

    def _validate_network_profiles(self, hostname):
        node_profiles = self.get_network_profiles(hostname)
        utils.validate_list_items_unique(profiles)
        netprofconf = self.confman.get_network_profiles_config_handler()
        netprofiles = netprofconf.get_network_profiles()
        for profile in node_profiles:
            if profile not in netprofiles:
                raise configerror.ConfigError('Invalid network profile %s specified for host %s' % (profile, hostname))

    def _validate_performance_profiles(self, hostname):
        node_performance_profiles = []
        try:
            node_performance_profiles = self.get_performance_profiles(hostname)
        except configerror.ConfigError:
            pass

        if node_performance_profiles:
            utils.validate_list_items_unique(node_performance_profiles)
            perfprofconf = self.confman.get_performance_profiles_config_handler()
            perfprofiles = perfprofconf.get_performance_profiles()
            for profile in node_performance_profiles:
                if profile not in perfprofiles:
                    raise configerror.ConfigError('Invalid performance profile %s specified for host %s' % (profile, hostname))

    def _validate_storage_profiles(self, hostname):
        node_storage_profiles = []
        try:
            node_storage_profiles = self.get_storage_profiles(hostname)
        except configerror.ConfigError:
            pass

        if node_storage_profiles:
            utils.validate_list_items_unique(node_storage_profiles)
            storageprofconf = self.confman.get_storage_profiles_config_handler()
            storageprofiles = storageprofconf.get_storage_profiles()
            for profile in node_storage_profiles:
                if profile not in storageprofiles:
                    raise configerror.ConfigError('Invalid storage profile %s specific for %s' % (profile, hostname))

    def get_hosts(self):
        """ get the list of hosts in the cloud

            Return:

            A sorted list of host names

            Raise:

            ConfigError in-case of an error
        """
        self.validate_root()

        return sorted(self.config[self.ROOT].keys())

    def get_labels(self, hostname):
        mandatory_labels = \
            {"nodetype": self.get_nodetype(hostname),
             "nodeindex": self.get_nodeindex(hostname),
             "nodename": self.get_nodename(hostname)}
        labels = self.config[self.ROOT][hostname].get('labels', {}).copy()
        labels.update(mandatory_labels)

        if self.is_sriov_enabled(hostname):
            labels.update({"sriov": "enabled"})

        black_list = ['name']
        return {name: attributes
                for name, attributes in labels.iteritems()
                if name not in black_list}

    def get_nodetype(self, hostname):
        service_profiles_lib = profiles.Profiles()
        service_profiles = self.get_service_profiles(hostname)

        if service_profiles_lib.get_caasmaster_service_profile() in service_profiles:
            return service_profiles_lib.get_caasmaster_service_profile()
        if service_profiles_lib.get_caasworker_service_profile() in service_profiles:
            return service_profiles_lib.get_caasworker_service_profile()

        return service_profiles[0]

    def set_noderole(self):
        hosts = self.get_hosts()
        for host in hosts:
            self.config[self.ROOT][host]['noderole'] = self.get_noderole(host)

    def set_nodeindex(self):
        hostsconf = self.confman.get_hosts_config_handler()
        install_host = utils.get_installation_host_name(hostsconf)
        self.config[self.ROOT][install_host]['caas_nodeindex'] = 1

        masters = self.get_service_profile_hosts('caas_master')
        masters.remove(install_host)
        self._set_nodeindexes(masters, 2)
        self._set_nodeindexes(self.get_service_profile_hosts('caas_worker'), 1)

    def _set_nodeindexes(self, hosts, base_index):
        index = base_index
        for host in hosts:
            self.config[self.ROOT][host]['caas_nodeindex'] = index
            index += 1

    def get_nodeindex(self, hostname):
        return self.config[self.ROOT][hostname]['caas_nodeindex']

    def get_nodename(self, hostname):
        return "{}{}".format(self.get_nodetype(hostname), self.get_nodeindex(hostname))

    def get_noderole(self, hostname):
        service_profiles_lib = profiles.Profiles()
        service_profiles = self.get_service_profiles(hostname)

        if service_profiles_lib.get_caasmaster_service_profile() in service_profiles:
            return "master"
        return "worker"

    def is_sriov_enabled(self, hostname):
        netprofs = self.get_network_profiles(hostname)
        netprofconf = self.confman.get_network_profiles_config_handler()
        for netprof in netprofs:
            if 'sriov_provider_networks' in self.config[netprofconf.ROOT][netprof]:
                return True
        return False

    def get_enabled_hosts(self):
        """ get the list of enabled hosts in the cloud

            Return:

            A list of host names

            Raise:

            ConfigError in-case of an error
        """
        self.validate_root()
        hosts = self.get_hosts()
        ret = []
        for host in hosts:
            if self.is_host_enabled(host):
                ret.append(host)
        return ret

    def get_hwmgmt_ip(self, hostname):
        """get the hwmgmt ip address

            Arguments:

            hostname: The name of the node

            Return:

            The BMC ip address as a string

            Raise:

            ConfigError in-case of an error
        """
        self._validate_hostname(hostname)

        if 'hwmgmt' not in self.config[self.ROOT][hostname] or 'address' not in self.config[self.ROOT][hostname]['hwmgmt']:
            raise configerror.ConfigError('No hwmgmt info defined for host')

        return self.config[self.ROOT][hostname]['hwmgmt']['address']

    def get_hwmgmt_user(self, hostname):
        """get the hwmgmt user

            Arguments:

            hostname: The name of the node

            Return:

            The BMC user name.

            Raise:

            ConfigError in-case of an error
        """
        self._validate_hostname(hostname)

        if 'hwmgmt' not in self.config[self.ROOT][hostname] or 'user' not in self.config[self.ROOT][hostname]['hwmgmt']:
            raise configerror.ConfigError('No hwmgmt info defined for host')

        return self.config[self.ROOT][hostname]['hwmgmt']['user']

    def get_hwmgmt_password(self, hostname):
        """get the hwmgmt password

           Arguments:

           hostname: The name of the node

           Return:

           The BMC password

           Raise:

           ConfigError in-case of an error
        """
        self._validate_hostname(hostname)

        if 'hwmgmt' not in self.config[self.ROOT][hostname] or 'password' not in self.config[self.ROOT][hostname]['hwmgmt']:
            raise configerror.ConfigError('No hwmgmt info defined for host')

        return self.config[self.ROOT][hostname]['hwmgmt']['password']

    def get_service_profiles(self, hostname):
        """get the node service profiles

           Arguments:

           hostname: The name of the node

           Return:

           A list containing service profile names

           Raise:

           ConfigError in-case of an error
        """
        self._validate_hostname(hostname)

        if 'service_profiles' not in self.config[self.ROOT][hostname]:
            raise configerror.ConfigError('No service profiles found')

        return self.config[self.ROOT][hostname]['service_profiles']

    def get_performance_profiles(self, hostname):
        """ get the performance profiles

            Arguments:

            hostname: The name of the node

            Return:

            A list containing the perfromance profile names.

            Raise:

            ConfigError in-case of an error
        """
        self._validate_hostname(hostname)

        if 'performance_profiles' not in self.config[self.ROOT][hostname]:
            raise configerror.ConfigError('No performance profiles found')

        return self.config[self.ROOT][hostname]['performance_profiles']

    def get_network_profiles(self, hostname):
        """get the node network profiles

           Arguments:

           hostname: The name of the node

           Return:

           A list containing network profile names

           Raise:

           ConfigError in-case of an error
        """
        self._validate_hostname(hostname)

        if 'network_profiles' not in self.config[self.ROOT][hostname]:
            raise configerror.ConfigError('No network profiles found')

        return self.config[self.ROOT][hostname]['network_profiles']

    def get_storage_profiles(self, hostname):
        """get the node storage profiles

           Arguments:

           hostname: The name of the node

           Return:

           A list containing storage profile names

           Raise:

           ConfigError in-case of an error
        """
        self._validate_hostname(hostname)

        if 'storage_profiles' not in self.config[self.ROOT][hostname]:
            raise configerror.ConfigError('No storage profiles found')

        return self.config[self.ROOT][hostname]['storage_profiles']

    def _validate_hostname(self, hostname):
        if not self.is_valid_host(hostname):
            raise configerror.ConfigError('Invalid hostname given %s' % hostname)

    def is_valid_host(self, hostname):
        """check if a host is valid

           Arguments:

           hostname: The name of the node

           Return:

           True or False

           Raise:

           ConfigError in-case of an error
        """
        self.validate_root()
        if hostname in self.config[self.ROOT]:
            return True
        return False

    def get_service_profile_hosts(self, profile):
        """ get hosts having some service profile

            Argument:

            service profile name

            Return:

            A list of host names

            Raise:

            ConfigError in-case of an error
        """
        hosts = self.get_hosts()
        result = []
        for host in hosts:
            node_profiles = self.get_service_profiles(host)
            if profile in node_profiles:
                result.append(host)

        return result

    def get_network_profile_hosts(self, profile):
        """ get hosts having some network profile

            Argument:

            network profile name

            Return:

            A list of host names

            Raise:

            ConfigError in-case of an error
        """
        hosts = self.get_hosts()
        result = []
        for host in hosts:
            node_network_profiles = self.get_network_profiles(host)
            if profile in node_network_profiles:
                result.append(host)
        if not result:
            raise configerror.ConfigError('No hosts found for profile %s' % profile)

        return result

    def get_performance_profile_hosts(self, profile):
        """ get hosts having some performance profile

            Argument:

            performance profile name

            Return:

            A list of host names

            Raise:

            ConfigError in-case of an error
        """
        hosts = self.get_hosts()
        result = []
        for host in hosts:
            node_performance_profiles = self.get_performance_profiles(host)
            if profile in node_performance_profiles:
                result.append(host)
        if not result:
            raise configerror.ConfigError('No hosts found for profile %s' % profile)

        return result

    def get_storage_profile_hosts(self, profile):
        """ get hosts having some storage profile

            Argument:

            storage profile name

            Return:

            A list of host names

            Raise:

            ConfigError in-case of an error
        """
        hosts = self.get_hosts()
        result = []
        for host in hosts:
            try:
                node_storage_profiles = self.get_storage_profiles(host)
                if profile in node_storage_profiles:
                    result.append(host)
            except configerror.ConfigError:
                pass

        if not result:
            raise configerror.ConfigError('No hosts found for profile %s' % profile)

        return result

    def get_host_network_interface(self, host, network):
        """ get the host interface used for some network

            Argument:

            the host name

            the network name

            Return:

            The interface name

            Raise:

            ConfigError in-case of an error
        """
        node_network_profiles = self.get_network_profiles(host)
        netprofconf = self.confman.get_network_profiles_config_handler()
        for profile in node_network_profiles:
            interfaces = netprofconf.get_profile_network_mapped_interfaces(profile)
            for interface in interfaces:
                networks = netprofconf.get_profile_interface_mapped_networks(profile, interface)
                if network in networks:
                    return interface

        raise configerror.ConfigError('No interfaces found for network %s in host %s' % (network, host))

    def get_host_network_ip_holding_interface(self, host, network):
        """ get the host ip holding interface some network

            Argument:

            the host name

            the network name

            Return:

            The interface name

            Raise:

            ConfigError in-case of an error
        """
        networkingconf = self.confman.get_networking_config_handler()
        vlan = None
        try:
            domain = self.get_host_network_domain(host)
            vlan = networkingconf.get_network_vlan_id(network, domain)
        except configerror.ConfigError as exp:
            pass

        if vlan:
            return 'vlan'+str(vlan)

        return self.get_host_network_interface(host, network)

    def get_host_networks(self, hostname):
        """ get the host networks

            Argument:

            The host name

            Return:

            A list of network names

            Raise:

            ConfigError in-case of an error
        """
        node_network_profiles = self.get_network_profiles(hostname)
        netprofconf = self.confman.get_network_profiles_config_handler()
        result = []
        for profile in node_network_profiles:
            interfaces = netprofconf.get_profile_network_mapped_interfaces(profile)
            for interface in interfaces:
                networks = netprofconf.get_profile_interface_mapped_networks(profile, interface)
                for network in networks:
                    if network not in result:
                        result.append(network)
        if not result:
            raise configerror.ConfigError('No networks found for host %s' % hostname)

        return result

    def get_host_having_hwmgmt_address(self, hwmgmtips):
        """ get the node name matching an ipmi address

            Argument:

            The ipmi address

            Return:

            The node name

            Raise:

            ConfigError in-case of an error
        """
        import ipaddress
        hosts = self.get_hosts()
        for host in hosts:
            ip = self.get_hwmgmt_ip(host)
            for hwmgtip in hwmgmtips:
                addr=ipaddress.ip_address(unicode(hwmgtip))
                if addr.version == 6:
                   hwmgtip=addr.compressed
                   ip=ipaddress.ip_address(unicode(ip))
                   ip=ip.compressed
                if ip == hwmgtip:
                   return host
        raise configerror.ConfigError('No hosts are matching the provided hw address %s' % hwmgmtips)

    def set_installation_host(self, name):
        """ set the installation node

            Argument:

            The installation node name

            Raise:

            ConfigError in-case of an error
        """
        self._validate_hostname(name)

        self.config[self.ROOT][name]['installation_host'] = True

    def is_installation_host(self, name):
        """ get if the node is an installation node

            Argument:

            The node name

            Return:

            True if installation node

            Raise:

            ConfigError in-case of an error
        """
        self._validate_hostname(name)

        if 'installation_host' in self.config[self.ROOT][name]:
            return self.config[self.ROOT][name]['installation_host']

        return False

    def get_installation_host(self):
        """ get the name of the node used for installation

            Return:

            The node name

            Raise:

            ConfigError in-case of an error
        """
        hosts = self.get_hosts()
        for host in hosts:
            if self.is_installation_host(host):
                return host

        raise configerror.ConfigError('No installation host found')

    def disable_host(self, host):
        """ disable the hosts visible via configuration.
            This can be used in bootstrapping phase.

            Argument:

            host to disable

            Raise:

            ConfigError in-case if provided host is not valid
        """
        self._validate_hostname(host)

        self.config[self.ROOT][host]['disabled'] = True

    def enable_host(self, host):
        """ enable  the hosts visible via configuration.
            This can be used in bootstrapping phase.

            Argument:

            host to enable

            Raise:

            ConfigError in-case if provided host is not valid
        """
        self._validate_hostname(host)

        self.config[self.ROOT][host]['disabled'] = False

    def is_host_enabled(self, host):
        """ is the host enabled

            Argument:

            the host to be checked

            Raise:

            ConfigError in-case if provided host is not valid
        """
        self._validate_hostname(host)

        if 'disabled' in self.config[self.ROOT][host]:
            return not self.config[self.ROOT][host]['disabled']

        return True

    def get_mgmt_mac(self, host):
        self._validate_hostname(host)

        if 'mgmt_mac' in self.config[self.ROOT][host]:
            return self.config[self.ROOT][host]['mgmt_mac']
        return []

    def get_host_network_domain(self, host):
        self._validate_hostname(host)
        if 'network_domain' not in self.config[self.ROOT][host]:
            raise configerror.ConfigError('Missing network domain for host %s' % host)
        return self.config[self.ROOT][host]['network_domain']

    def get_controllers_network_domain(self):
        controllers = self.get_service_profile_hosts('controller')
        domains = set()
        for controller in controllers:
            domains.add(self.get_host_network_domain(controller))

        if len(domains) != 1:
            raise configerror.ConfigError('Controllers in different networking domains not supported')
        return domains.pop()

    def get_managements_network_domain(self):
        managements = self.get_service_profile_hosts('management')
        domains = set()
        for management in managements:
            domains.add(self.get_host_network_domain(management))
        if len(domains) != 1:
            raise configerror.ConfigError('Management in different networking domains not supported')
        return domains.pop()

    def update_service_profiles(self):
        profs = profiles.Profiles()
        hosts = self.get_hosts()
        for host in hosts:
            new_profiles = []
            current_profiles = self.config[self.ROOT][host]['service_profiles']
            new_profiles = current_profiles
            for profile in current_profiles:
                included_profiles = profs.get_included_profiles(profile)
                new_profiles = utils.add_lists(new_profiles, included_profiles)
            self.config[self.ROOT][host]['service_profiles'] = new_profiles

    def get_pre_allocated_ips(self, host, network):
        ips_field = "pre_allocated_ips"
        self._validate_hostname(host)
        if (ips_field not in self.config[self.ROOT][host]
                or network not in self.config[self.ROOT][host][ips_field]):
            return None
        return self.config[self.ROOT][host][ips_field][network]

    def allocate_port(self, host, base, name):
        used_ports = []
        hosts = self.get_hosts()
        for node in hosts:
            if name in self.config[self.ROOT][node]:
                used_ports.append(self.config[self.ROOT][node][name])

        free_port = 0

        for port in range(base, base+1000):
            if port not in used_ports:
                free_port = port
                break

        if free_port == 0:
            raise configerror.ConfigError('No free ports available')

        self.config[self.ROOT][host][name] = free_port

    def add_vbmc_port(self, host):
        base_vbmc_port = 61600
        name = 'vbmc_port'
        self._validate_hostname(host)
        if name not in self.config[self.ROOT][host]:
            self.allocate_port(host, base_vbmc_port, name)

    def add_ipmi_terminal_port(self, host):
        base_console_port = 61401
        name = 'ipmi_terminal_port'
        self._validate_hostname(host)
        if name not in self.config[self.ROOT][host]:
            self.allocate_port(host, base_console_port, name)

    def get_ceph_osd_disks(self, host):
        self._validate_hostname(host)
        caas_disks = self.config[self.ROOT][host].get('caas_disks', [])
        osd_disks = filter(lambda disk: disk.get('osd_disk', False), caas_disks)
        return map(lambda disk: _get_path_for_virtio_id(disk), osd_disks)

    def get_system_reserved_memory(self, hostname):
        caasconf = self.confman.get_caas_config_handler()
        if caasconf.is_vnf_embedded_deployment():
            return VNF_EMBEDDED_RESERVED_MEMORY

        profiles = self.get_service_profiles(hostname)
        if 'controller' in profiles:
            return DUAL_VIM_CONTROLLER_RESERVED_MEMORY
        if 'compute' in profiles:
            return DUAL_VIM_DEFAULT_RESERVED_MEMORY

        return self.config.get(self.ROOT, {}).get('middleware_reserved_memory',
                                                   MIDDLEWARE_RESERVED_MEMORY)

    def set_default_reserved_memory_to_all_hosts(self, def_memory):
        for host in self.get_hosts():
            self.config[self.ROOT][host]['middleware_reserved_memory'] = def_memory

    def set_default_ipmi_priv_level_to_all_hosts(self, def_priv):
        for host in self.get_hosts():
            if 'hwmgmt' not in self.config[self.ROOT][host]:
                self.config[self.ROOT][host]['hwmgmt'] = {'priv_level': def_priv}
            elif 'priv_level' not in self.config[self.ROOT][host]['hwmgmt']:
                self.config[self.ROOT][host]['hwmgmt']['priv_level'] = def_priv


def _get_path_for_virtio_id(disk):
    disk_id = disk.get('id', '')
    if disk_id:
        return "/dev/disk/by-id/virtio-{}".format(disk_id[:20])


