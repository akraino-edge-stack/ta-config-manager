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
from __future__ import print_function
import json
import os

from cmframework.apis import cmerror
from cmframework.utils.cmpluginloader import CMPluginLoader
from cmdatahandlers.api import configmanager
from cmdatahandlers.api import utils
from serviceprofiles import profiles


class AnsibleInventory(object):

    def __init__(self, properties, plugin_path):
        self.pluginloader = AnsibleInventoryPluginLoader(plugin_path)
        self.props = properties
        propsjson = {}
        for name, value in properties.iteritems():
            try:
                propsjson[name] = json.loads(value)
            except Exception:  # pylint: disable=broad-except
                continue
        self.confman = configmanager.ConfigManager(propsjson)

    # pylint: disable=no-self-use
    def _is_setup(self):
        if 'CONFIG_PHASE' in os.environ and os.environ['CONFIG_PHASE'] == 'setup':
            return True
        return False

    def _is_bootstrapping(self):
        if 'CONFIG_PHASE' in os.environ and os.environ['CONFIG_PHASE'] == 'bootstrapping':
            return True
        return False

    def _is_provisioning(self):
        if 'CONFIG_PHASE' in os.environ and os.environ['CONFIG_PHASE'] == 'provisioning':
            return True
        return False

    def _is_postconfig(self):
        if not self._is_bootstrapping() and not self._is_provisioning():
            return True
        return False

    def _get_own_host(self):

        hostsconf = self.confman.get_hosts_config_handler()

        if utils.is_virtualized():
            return hostsconf.get_installation_host()

        hwmgmtip = utils.get_own_hwmgmt_ip()

        return hostsconf.get_host_having_hwmgmt_address(hwmgmtip)

    def set_default_route(self, hostvars, node, infra_internal_name):
        routes = hostvars[node]['networking'][infra_internal_name].get('routes', [])
        infra_int_ip = hostvars[node]['networking'][infra_internal_name]['ip']
        caasconf = self.confman.get_caas_config_handler()
        cidr_to_set = caasconf.get_caas_parameter("service_cluster_ip_cidr")
        routes.append({"to": cidr_to_set, "via": infra_int_ip})
        hostvars[node]['networking'][infra_internal_name]['routes'] = routes

    def set_common_caas(self, hostvars, node, hostsconf):
        hostvars[node]['nodetype'] = hostsconf.get_nodetype(node)
        hostvars[node]['nodeindex'] = hostsconf.get_nodeindex(node)
        hostvars[node]['nodename'] = hostsconf.get_nodename(node)

        host_labels = hostsconf.get_labels(node)
        if host_labels:
            hostvars[node]['labels'] = host_labels

        hostvars[node]['ssl_alt_name'] = {}
        dns = [node]
        hostvars[node]['ssl_alt_name']['dns'] = dns
        ips = ['127.0.0.1']
        ips.append(hostvars[node]['ansible_host'])
        hostvars[node]['ssl_alt_name']['ip'] = ips

    def set_caas_master_data(self, hostvars, node, caasconf, hostsconf):
        dns = hostvars[node]['ssl_alt_name']['dns']
        dns.append(caasconf.get_kubernetes_domain())
        dns.append(caasconf.get_apiserver_in_hosts())
        dns.append(caasconf.get_registry_url())
        dns.append(caasconf.get_update_registry_url())
        dns.append(caasconf.get_swift_url())
        dns.append(caasconf.get_swift_update_url())
        dns.append(caasconf.get_ldap_master_url())
        dns.append(caasconf.get_ldap_slave_url())
        dns.append(caasconf.get_chart_repo_url())
        dns.append(caasconf.get_caas_parameter('prometheus_url'))
        dns.append(caasconf.get_tiller_url())

        hosts = hostsconf.get_hosts()
        for host in hosts:
            if 'caas_master' in hostsconf.get_service_profiles(host):
                dns.append(host)

        hostvars[node]['ssl_alt_name']['dns'] = dns
        ips = hostvars[node]['ssl_alt_name']['ip']
        ips.append(caasconf.get_apiserver_svc_ip())
        hostvars[node]['ssl_alt_name']['ip'] = ips

    def generate_inventory(self):
        try:
            inventory = {}

            # convert properties to inventory using the following rules:
            # 1. cloud scoped configuration is mapped to "all" group's "vars" section
            # 2. The host level domain configuration will be mapped to "_meta" section
            #    under "hostvars" group. Under this there will be a dictionary per host.
            # 3. The mapping between hosts and profiles is created.
            #    This is used to allow ansible to automatically identify in which hosts
            #    the playbooks are to be run.
            #    This mapping is done as follows:
            #      - A mapping is created for each service profile.
            #      - A mapping is created for the network_profiles type.
            #      - A mapping is created for the storage_profiles type.
            #      - A mapping is created for the performance_profiles type.

            # Get the host variables and all variables
            hostvars = {}
            allvars = {}

            netconf = self.confman.get_networking_config_handler()
            hostsconf = self.confman.get_hosts_config_handler()
            infra_internal_name = netconf.get_infra_internal_network_name()
            hosts = hostsconf.get_hosts()

            ownhost = self._get_own_host()
            if self._is_bootstrapping():
                for host in hosts:
                    if host != ownhost:
                        hostsconf.disable_host(host)

            hosts = hostsconf.get_enabled_hosts()
            for name, value in self.props.iteritems():
                try:
                    d = name.split('.')
                    if len(d) != 2:
                        continue
                    node = d[0]
                    domain = d[1]
                    if node != 'cloud':
                        if node in hosts:
                            if node not in hostvars:
                                hostvars[node] = {}
                            hostip = netconf.get_host_ip(node, infra_internal_name)
                            hostvars[node]['ansible_host'] = hostip

                            try:
                                hostvars[node][domain] = json.loads(value)
                            except Exception:  # pylint: disable=broad-except
                                hostvars[node][domain] = value

                            if 'caas_master' in hostsconf.get_service_profiles(node):
                                self.set_common_caas(hostvars, node, hostsconf)
                                caasconf = self.confman.get_caas_config_handler()
                                self.set_caas_master_data(hostvars, node, caasconf, hostsconf)
                                self.set_default_route(hostvars, node, infra_internal_name)

                            if 'caas_worker' in hostsconf.get_service_profiles(node):
                                self.set_common_caas(hostvars, node, hostsconf)
                                self.set_default_route(hostvars, node, infra_internal_name)
                    else:
                        try:
                            allvars[domain] = json.loads(value)
                        except Exception:  # pylint: disable=broad-except
                            allvars[domain] = value

                except Exception:  # pylint: disable=broad-except
                    pass

            inventory['_meta'] = {}
            inventory['_meta']['hostvars'] = hostvars
            inventory['all'] = {'vars': allvars}

            # add hosts to service profiles mapping
            serviceprofiles = profiles.Profiles().get_service_profiles()
            for profile in serviceprofiles:
                try:
                    servicehosts = hostsconf.get_service_profile_hosts(profile)
                    tmp = []
                    for host in servicehosts:
                        if host in hosts:
                            tmp.append(host)
                    inventory[profile] = tmp
                except Exception:  # pylint: disable=broad-except
                    continue

            # add mapping between profile types and hosts
            inventory['network_profiles'] = []
            inventory['storage_profiles'] = []
            inventory['performance_profiles'] = []
            for host in hosts:
                # check for network profiles
                try:
                    _ = hostsconf.get_network_profiles(host)
                    inventory['network_profiles'].append(host)
                except Exception:  # pylint: disable=broad-except
                    pass

                # check for storage profiles
                try:
                    _ = hostsconf.get_storage_profiles(host)
                    inventory['storage_profiles'].append(host)
                except Exception:  # pylint: disable=broad-except
                    pass

                # check for perfromance profiles
                try:
                    _ = hostsconf.get_performance_profiles(host)
                    inventory['performance_profiles'].append(host)
                except Exception:  # pylint: disable=broad-except
                    pass

            self.pluginloader.load()
            plugins = self.pluginloader.get_plugin_instances(self.confman, inventory, ownhost)
            if self._is_setup():
                inventory.clear()
            for name, plugin in sorted(plugins.iteritems()):
                if self._is_bootstrapping():
                    plugin.handle_bootstrapping()
                elif self._is_provisioning():
                    plugin.handle_provisioning()
                elif self._is_setup():
                    plugin.handle_setup()
                else:
                    plugin.handle_postconfig()

            return inventory

        except Exception as exp:  # pylint: disable=broad-except
            raise cmerror.CMError(str(exp))


class AnsibleInventoryPluginLoader(CMPluginLoader):
    def __init__(self, plugin_location, plugin_filter=None):
        super(AnsibleInventoryPluginLoader, self).__init__(plugin_location, plugin_filter)

    def build_filter_dict(self):
        pass

    def get_plugin_instances(self, confman, inventory, ownhost):
        plugs = {}
        for plugin, module in self.loaded_plugin.iteritems():
            class_name = getattr(module, plugin)
            instance = class_name(confman, inventory, ownhost)
            plugs[plugin] = instance
        return plugs


def main():
    import argparse
    import sys
    import traceback

    parser = argparse.ArgumentParser(description='Test ansible inventory handler', prog=sys.argv[0])

    parser.add_argument('--properties',
                        required=True,
                        dest='properties',
                        metavar='PROPERTIES',
                        help='The file containing the properties',
                        type=str,
                        action='store')

    parser.add_argument('--plugins',
                        required=True,
                        dest='plugins',
                        metavar='PLUGINS',
                        help='The path to ansible inventory plugin(s)',
                        type=str,
                        action='store')

    try:
        args = parser.parse_args(sys.argv[1:])

        f = open(args.properties, 'r')
        lines = f.read().splitlines()
        f.close()
        properties = {}
        for line in lines:
            d = line.split('=')
            if len(d) != 2:
                continue
            properties[d[0]] = d[1]
        ansible = AnsibleInventory(properties, args.plugins)
        inventory = ansible.generate_inventory()

        print(json.dumps(inventory, indent=4, sort_keys=True))

    except Exception as exp:  # pylint: disable=broad-except
        print(str(exp))
        traceback.print_exc()
        sys.exit(1)
    sys.exit(0)


if __name__ == '__main__':
    main()
