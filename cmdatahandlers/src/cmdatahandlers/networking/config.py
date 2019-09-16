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
from serviceprofiles import profiles
from netaddr import IPNetwork, IPSet, IPRange


VALID_NETWORKS = [
    'caas_oam',
    'cloud_tenant',
    'infra_access',
    'infra_external',
    'infra_internal',
    'infra_hw_management',
    'infra_storage_cluster',
]

NETWORK_DOMAINS = 'network_domains'


class Config(config.Config):
    def __init__(self, confman):
        super(Config, self).__init__(confman)
        self.ROOT = 'cloud.networking'
        self.DOMAIN = 'networking'
        self.freepool = {}
        self.external_vip = None

    def init(self):
        if self.ROOT not in self.config:
            return
        try:
            # a mapping between network and free IPSet
            self.freepool = {}
            for network in self.config[self.ROOT].keys():
                if network in VALID_NETWORKS:
                    if NETWORK_DOMAINS not in self.config[self.ROOT][network]:
                        raise configerror.ConfigError('No network domains for network %s' % network)

                    self.freepool[network] = {}
                    for domain in self.config[self.ROOT][network][NETWORK_DOMAINS].keys():
                        self.freepool[network][domain] = self._get_free_set(network, domain)

        except configerror.ConfigError:
            raise

        except Exception as exp:
            raise configerror.ConfigError(str(exp))

    def _validate_network(self, network, domain=None):
        networks = self.get_networks()
        if network not in networks:
            raise configerror.ConfigError('Invalid network name %s' % network)

        if NETWORK_DOMAINS not in self.config[self.ROOT][network]:
            raise configerror.ConfigError('No network domains for network %s' % network)

        if domain and domain not in self.config[self.ROOT][network][NETWORK_DOMAINS]:
            raise configerror.ConfigError('Invalid network domain name %s' % domain)

    def _get_free_set(self, network, domain):
        ip_range_start = self.get_network_ip_range_start(network, domain)
        ip_range_end = self.get_network_ip_range_end(network, domain)
        select_range = IPRange(ip_range_start, ip_range_end)
        netset = IPSet(select_range)
        if (network == self.get_infra_external_network_name() and
                domain == self._get_vip_domain()):
            iterator = netset.__iter__()
            self.external_vip = str(iterator.next())
            netset.remove(self.external_vip)

        # check for the IP(s) taken by the nodes
        try:
            hostsconfig = self.confman.get_hosts_config_handler()
            hosts = hostsconfig.get_hosts()
            for host in hosts:
                try:
                    hostip = self.get_host_ip(host, network)
                    netset.remove(hostip)
                except configerror.ConfigError:
                    pass
        except configerror.ConfigError:
            pass

        service_profiles_lib = profiles.Profiles()

        # check for the IP(s) taken as VIPs
        if network == self.get_infra_internal_network_name() and domain == self._get_vip_domain():
            vips = self.get_net_vips(network)
            for _, vip in vips.iteritems():
                try:
                    netset.remove(vip)
                except configerror.ConfigError:
                    pass

        return netset

    def get_dns(self):
        """ get the list of dns servers

            Return:

            A list of dns servers

            Raise:

            ConfigError is raised in-case of an error
        """
        self.validate_root()
        if 'dns' not in self.config[self.ROOT]:
            raise configerror.ConfigError('dns not found!')

        return self.config[self.ROOT]['dns']

    def get_mtu(self):
        """ get the mtu value

            Return:

            A number representing the mtu size

            Raise:

            ConfigError is raised in-case of an error
        """
        self.validate_root()
        if 'mtu' not in self.config['cloud.networking']:
            raise configerror.ConfigError('mtu not found!')
        return self.config[self.ROOT]['mtu']

    def get_networks(self):
        """ get the list of network names

            Return:

            A list of network names

            Raise:

            ConfigError is raised in-case of an error
        """
        self.validate_root()
        networks = []
        for entry in self.config[self.ROOT]:
            if entry in VALID_NETWORKS:
                networks.append(entry)
        return networks

    def allocate_ip(self, network, domain):
        """ get a new free ip in some network

            Arguments:

            Network name

            Network domain

            Return:

            The free ip address

            Raise:

            ConfigError in-case of an error
        """
        self._validate_network(network, domain)

        try:
            iterator = self.freepool[network][domain].__iter__()
            ip = str(iterator.next())
            self.freepool[network][domain].remove(ip)
            return ip
        except Exception:
            raise configerror.ConfigError('Failed to allocate ip for network %s in %s' % (network, domain))

    def allocate_static_ip(self, ip, network, domain=None):
        """ allocate the given ip in some network

            Arguments:

            Ip address

            Network name

            Network domain

            Return:

            The allocated ip address

            Raise:

            ConfigError in-case of an error
        """
        self._validate_network(network, domain)

        try:
            self.freepool[network][domain].remove(ip)
            return ip
        except Exception:
            raise configerror.ConfigError('Failed to allocate %s for network %s in %s' % (ip, network, domain))

    def allocate_vip(self, network):
        return self.allocate_ip(network, self._get_vip_domain())

    def get_network_domains(self, network):
        self._validate_network(network)
        return self.config[self.ROOT][network][NETWORK_DOMAINS].keys()

    def get_network_cidr(self, network, domain):
        """ get the network cidr

            Arguments:

            Network name

            Network domain

            Return:

            The cidr address

            Raise:

            ConfigError in-case of an error
        """
        self._validate_network(network, domain)

        if 'cidr' not in self.config[self.ROOT][network][NETWORK_DOMAINS][domain]:
            raise configerror.ConfigError('No CIDR for network %s in %s' % (network, domain))

        return self.config[self.ROOT][network][NETWORK_DOMAINS][domain]['cidr']

    def get_vip_network_cidr(self, network):
        return self.get_network_cidr(network, self._get_vip_domain())

    def get_network_mask(self, network, domain):
        """ get the network mask

            Arguments:

            Network name

            Network domain

            Return:

            A number representing the mask

            Raise:

            ConfigError in-case of an error
        """
        cidr = self.get_network_cidr(network, domain)
        try:
            mask = cidr.split('/')[1]
            return int(mask)
        except Exception as exp:
            raise configerror.ConfigError('Invalid network mask in %s: %s' % (cidr, str(exp)))

    def get_vip_network_mask(self, network):
        return self.get_network_mask(network, self._get_vip_domain())

    def get_network_gateway(self, network, domain):
        """ get the network gateway

            Arguments:

            Network name

            Network domain

            Return:

            The gateway address

            Raise:

            ConfigError in-case of an error
        """
        self._validate_network(network, domain)

        if 'gateway' not in self.config[self.ROOT][network][NETWORK_DOMAINS][domain]:
            raise configerror.ConfigError('No gateway configured for network %s in %s' % (network, domain))

        return self.config[self.ROOT][network][NETWORK_DOMAINS][domain]['gateway']

    def get_network_routes(self, network, domain):
        self._validate_network(network, domain)

        if 'routes' not in self.config[self.ROOT][network][NETWORK_DOMAINS][domain]:
            raise configerror.ConfigError('No routes configured for network %s in %s' % (network, domain))

        return self.config[self.ROOT][network][NETWORK_DOMAINS][domain]['routes']

    def get_network_ip_range_start(self, network, domain):
        """ get the network allocation range start

            Arguments:

            Network name

            Network domain

            Return:

            The starting allocation range

            Raise:

            ConfigError in-case of an error
        """
        net = IPNetwork(self.get_network_cidr(network, domain))

        if 'ip_range_start' in self.config[self.ROOT][network][NETWORK_DOMAINS][domain]:
            return self.config[self.ROOT][network][NETWORK_DOMAINS][domain]['ip_range_start']
        else:
            return str(net[1])

    def get_network_ip_range_end(self, network, domain):
        """ get the network allocation range end

            Arguments:

            Network name

            Network domain

            Return:

            The end of the allocation range

            Raise:

            ConfigError in-case of an error
        """
        net = IPNetwork(self.get_network_cidr(network, domain))

        if 'ip_range_end' in self.config[self.ROOT][network][NETWORK_DOMAINS][domain]:
            return self.config[self.ROOT][network][NETWORK_DOMAINS][domain]['ip_range_end']
        else:
            return str(net[-2])

    def get_network_vlan_id(self, network, domain):
        """ get the network vlan id

            Arguments:

            Network name

            Network domain

            Return:

            The vlan id

            Raise:

            ConfigError in-case of an error
        """
        self._validate_network(network, domain)

        if 'vlan' not in self.config[self.ROOT][network][NETWORK_DOMAINS][domain]:
            raise configerror.ConfigError('No vlan specified for %s in %s' % (network, domain))

        return self.config[self.ROOT][network][NETWORK_DOMAINS][domain]['vlan']

    def get_vip_network_vlan_id(self, network):
        return self.get_network_vlan_id(network, self._get_vip_domain())

    def get_network_mtu(self, network):
        """ get the network mtu

            Argument:

            Network name

            Return:

            The mtu of the network

            Raise:

            ConfigError in-case of an error
        """
        self._validate_network(network)

        if 'mtu' not in self.config[self.ROOT][network]:
            raise configerror.ConfigError('No mtu specified for %s' % network)

        return self.config[self.ROOT][network]['mtu']

    def get_host_ip(self, host, network):
        """ get the host ip allocated from a specific network

            Argument:

            hostname: The name of the host
            networkname: The name of the network

            Return:

            The ip address assigned for the host

            Raise:

            ConfigError in-case of an error
        """
        self._validate_network(network)

        hostnetconfigkey = host + '.' + self.DOMAIN
        if hostnetconfigkey not in self.config:
            raise configerror.ConfigError('No network configuration available for %s' % host)

        if network not in self.config[hostnetconfigkey]:
            raise configerror.ConfigError('No network configuration available for %s' % host)

        if 'ip' not in self.config[hostnetconfigkey][network]:
            raise configerror.ConfigError('No IP assigned for %s in network %s' % (host, network))

        return self.config[hostnetconfigkey][network]['ip']

    def _get_vip_domain(self):
        return self.confman.get_hosts_config_handler().get_managements_network_domain()

    @staticmethod
    def get_infra_external_network_name():
        """ get the network name for the external network

            Return:

            The external network name

            Raise:

            ConfigError in-case the network is not configured
        """
        return 'infra_external'

    @staticmethod
    def get_infra_storage_cluster_network_name():
        """ get the infra storage cluster network name

            Return:

            The infra stroage cluster network name

            Raise:

            ConfigError in-case the network is not configured
        """
        return 'infra_storage_cluster'

    @staticmethod
    def get_hwmgmt_network_name():
        """ get the hwmgmt network name

            Return:

            The hwmgmt network name

            Raise:

            ConfigError in-case the network is not defined
        """
        return 'infra_hw_management'

    @staticmethod
    def get_infra_internal_network_name():
        """ get the infra management network name

            Return:

            The infra management network name

            Raise:

            ConfigError in-case the network is not defined
        """
        return 'infra_internal'

    @staticmethod
    def get_caas_oam_network_name():
        """ get the CaaS OAM network name

            Return:

            The CaaS OAM network name

            Raise:

        """
        return 'caas_oam'

    def get_cloud_tenant_network_name(self):
        """ get the network name for the cloud tenant network

            Return:

            The cloud tenant network name

            Raise:

            ConfigError in-case the network is not configured
        """
        return 'cloud_tenant'

    def get_infra_access_network_name(self):
        """ get the network name for the infra access network

            Return:

            The infra access network name

            Raise:

            ConfigError in-case the network is not configured
        """
        return 'infra_access'

    def add_host_networks(self, host):
        """ add host network data

            Argument:

            Host name

            Raise:

            ConfigError in-case of an error
        """
        hostsconf = self.confman.get_hosts_config_handler()
        networks = hostsconf.get_host_networks(host)
        domain = hostsconf.get_host_network_domain(host)
        for network in networks:
            try:
                ip = self.get_host_ip(host, network)
                continue
            except configerror.ConfigError:
                pass

            static_ip = hostsconf.get_pre_allocated_ips(host, network)
            if static_ip:
                ip = self.allocate_static_ip(static_ip, network, domain)
            else:
                ip = self.allocate_ip(network, domain)
            interface = hostsconf.get_host_network_ip_holding_interface(host, network)
            netmask = self.get_network_mask(network, domain)
            networkdata = {'ip': ip, 'interface': interface, 'mask': netmask}

            try:
                vlan = self.get_network_vlan_id(network, domain)
                networkdata['vlan'] = vlan
            except configerror.ConfigError:
                pass

            try:
                gw = self.get_network_gateway(network, domain)
                networkdata['gateway'] = gw
            except configerror.ConfigError:
                pass

            try:
                routes = self.get_network_routes(network, domain)
                networkdata['routes'] = routes
            except configerror.ConfigError:
                pass

            try:
                cidr = self.get_network_cidr(network, domain)
                networkdata['cidr'] = cidr
            except configerror.ConfigError:
                pass

            key = host + '.' + self.DOMAIN
            if key not in self.config:
                self.config[key] = {}
            if network not in self.config[key]:
                self.config[key][network] = {}

            self.config[key][network] = networkdata

    def delete_host_networks(self, host):
        """ delete host network data

            Argument:

            Host name
        """
        key = '{}.{}'.format(host, self.DOMAIN)
        if key in self.config:
            del self.config[key]

    def get_networking_hosts(self):
        """ get hosts with networking data

        Return:

        List of host names with existing networking data
        """
        hosts = []
        match = r'^[^.]*\.networking$'
        for key in self.config.keys():
            if key != self.ROOT and re.match(match, key):
                hosts.append(key.split('.')[0])
        return hosts

    def get_host_interface(self, host, network):
        """ get the host interface allocated from a specific network

            Argument:

            hostname: The name of the host
            networkname: The name of the network

            Return:

            The interface for the host

            Raise:

            ConfigError in-case of an error
        """
        self._validate_network(network)

        hostnetconfigkey = host + '.' + self.DOMAIN
        if hostnetconfigkey not in self.config:
            raise configerror.ConfigError('No network configuration available for %s' % host)

        if network not in self.config[hostnetconfigkey]:
            raise configerror.ConfigError('No network configuration available for %s' % host)

        if 'interface' not in self.config[hostnetconfigkey][network]:
            raise configerror.ConfigError(
                'No interface assigned for %s in network %s' % (host, network))

        return self.config[hostnetconfigkey][network]['interface']

    def get_host_mask(self, host, network):
        """ get the network mask for the host

            Argument:

            hostname: The name of the host
            networkname: The name of the network

            Return:

            The network mask

            Raise:

            ConfigError in-case of an error
        """
        self._validate_network(network)

        hostnetconfigkey = host + '.' + self.DOMAIN
        if hostnetconfigkey not in self.config:
            raise configerror.ConfigError('No network configuration available for %s' % host)

        if network not in self.config[hostnetconfigkey]:
            raise configerror.ConfigError('No network configuration available for %s' % host)

        if 'mask' not in self.config[hostnetconfigkey][network]:
            raise configerror.ConfigError('No mask assigned for %s in network %s' % (host, network))

        return self.config[hostnetconfigkey][network]['mask']

    def get_external_vip(self):
        """ get the external vip ip, this is always the first ip in the range
        """
        return self.external_vip

    def get_provider_networks(self):
        """
        Get provider network names

        Returns:
            A list of provider network names

        Raises:
            ConfigError in-case of an error
        """
        if 'provider_networks' not in self.config[self.ROOT]:
            raise configerror.ConfigError('No provider networks configured')

        return self.config[self.ROOT]['provider_networks'].keys()

    def is_shared_provider_network(self, network):
        """
        Is shared provider network

        Arguments:
            Provider network name

        Returns:
            True if given provider network is shared, False otherwise

        Raises:
            ConfigError in-case of an error
        """
        networks = self.get_provider_networks()
        if network not in networks:
            raise configerror.ConfigError('Missing configuration for provider network %s' % network)

        return (self.config[self.ROOT]['provider_networks'][network].get('shared') is True)

    def get_provider_network_vlan_ranges(self, network):
        """
        Get vlan ranges for the given provider network

        Arguments:
            Provider network name

        Returns:
            Vlan ranges for the provider network

        Raises:
            ConfigError in-case of an error
        """
        networks = self.get_provider_networks()
        if network not in networks:
            raise configerror.ConfigError('Missing configuration for provider network %s' % network)

        if 'vlan_ranges' not in self.config[self.ROOT]['provider_networks'][network]:
            raise configerror.ConfigError(
                'Missing vlan ranges configuration for provider network %s' % network)

        return self.config[self.ROOT]['provider_networks'][network]['vlan_ranges']

    def get_provider_network_mtu(self, network):
        """
        Get mtu for the given provider network

        Arguments:
            Provider network name

        Returns:
            mtu for the provider network

        Raises:
            ConfigError in-case of an error
        """
        networks = self.get_provider_networks()
        if network not in networks:
            raise configerror.ConfigError('Missing configuration for provider network %s' % network)

        if 'mtu' not in self.config[self.ROOT]['provider_networks'][network]:
            raise configerror.ConfigError(
                'Missing mtu configuration for provider network %s' % network)

        return self.config[self.ROOT]['provider_networks'][network]['mtu']

    def is_l3_ha_enabled(self):
        """ is L3 HA enabled

            Return:

            True if L3 HA is enabled, False otherwise
        """
        return True if 'l3_ha' in self.config[self.ROOT] else False

    def _get_l3_ha_config(self):
        if 'l3_ha' not in self.config[self.ROOT]:
            raise configerror.ConfigError('Missing L3 HA configuration')

        return self.config[self.ROOT]['l3_ha']

    def get_l3_ha_provider_network(self):
        """ get L3 HA provider network

            Return:

            L3 HA provider network name

            Raise:

            ConfigError in-case of an error
        """
        conf = self._get_l3_ha_config()
        if 'provider_network' not in conf:
            raise configerror.ConfigError('Missing L3 HA provider network configuration')

        return conf['provider_network']

    def get_l3_ha_cidr(self):
        """ get L3 HA CIDR

            Return:

            L3 HA CIDR

            Raise:

            ConfigError in-case of an error
        """
        conf = self._get_l3_ha_config()
        if 'cidr' not in conf:
            raise configerror.ConfigError('Missing L3 HA CIDR configuration')

        return conf['cidr']

    def add_ovs_config_defaults(self, host):
        """ Add Openvswitch default config """

        ovs_defaults = { 'tx-flush-interval': 0, 'rxq-rebalance': 0 }

        key = self.ROOT
        if key not in self.config:
            self.config[key] = {}
        if 'ovs_config' not in self.config[key]:
            self.config[key]['ovs_config'] = {}
        if host not in self.config[key]['ovs_config']:
            self.config[key]['ovs_config'][host] = {}

        self.config[key]['ovs_config'][host] = ovs_defaults

    def del_ovs_config(self, host):
        """ Delete Openvswitch config """
        if host in self.config[self.ROOT]['ovs_config']:
            self.config[self.ROOT]['ovs_config'].pop(host, None)

    def get_ovs_config(self, host):
        return self.config[self.ROOT]['ovs_config'].get(host, None)

    def _validate_ovs_config_args(self, host, args):
        ovs_conf = self.config[self.ROOT]['ovs_config']

        if args.get('tx_flush_interval') is not None:
            if int(args['tx_flush_interval']) >= 0 and int(args['tx_flush_interval']) <= 1000000:
                ovs_conf[host]['tx-flush-interval'] = int(args['tx_flush_interval'])
            else:
                raise ValueError("tx-flush-interval value must be 0..1000000")

        if args.get('rxq_rebalance_interval') is not None:
            if int(args['rxq_rebalance_interval']) >= 0 and int(args['rxq_rebalance_interval']) <= 1000000:
                ovs_conf[host]['rxq-rebalance'] = int(args['rxq_rebalance_interval'])
            else:
                raise ValueError("rxq_rebalance_interval value must be 0..1000000")

    def update_ovs_config(self, host, args):
        if self.config[self.ROOT]['ovs_config'].get(host, None) is None:
            return None
        self._validate_ovs_config_args(host, args)
        return self.config[self.ROOT]

    def get_ovs_config_hosts(self):
        return [host for host in self.config[self.ROOT]['ovs_config']]

    def add_vip(self, network, name, ip):
        if 'vips' not in self.config[self.ROOT]:
            self.config[self.ROOT]['vips'] = {}

        if network not in self.config[self.ROOT]['vips']:
            self.config[self.ROOT]['vips'][network] = {}

        self.config[self.ROOT]['vips'][network][name] = ip

    def add_external_vip(self):
        external_vip = self.get_external_vip()
        self.add_vip('infra_external', 'external_vip', external_vip)

    def add_internal_vip(self):
        internal_vip = self.allocate_vip('infra_internal')
        self.add_vip('infra_internal', 'internal_vip', internal_vip)

    def get_internal_vip(self):
        try:
            return self.config[self.ROOT]['vips']['infra_internal']['internal_vip']
        except KeyError as exp:
            raise configerror.ConfigError('Internal vip not found')

    def get_vips(self):
        if 'vips' not in self.config[self.ROOT]:
            return {}

        return self.config[self.ROOT]['vips']

    def get_net_vips(self, net):
        if 'vips' not in self.config[self.ROOT]:
            return {}

        if net not in self.config[self.ROOT]['vips']:
            return {}

        return self.config[self.ROOT]['vips'][net]

        return self.config[self.ROOT]['vips']
