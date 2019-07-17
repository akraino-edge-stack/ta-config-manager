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

import socket
import netaddr
import subprocess
import json

from cmdatahandlers.api import configerror

def validate_ipv4_address(address):
    try:
        socket.inet_pton(socket.AF_INET, address)
    except AttributeError:
        try:
            socket.inet_aton(address)
        except socket.error:
            raise configerror.ConfigError('Invalid ip %s' % address)
        if address.count('.') != 3:
            raise configerror.ConfigError('Invalid ip %s' % address)
    except socket.error:
        raise configerror.ConfigError('Invalid ip %s' % address)


def validate_list_items_unique(l):
    if len(l) != len(set(l)):
        raise configerror.ConfigError('List is not unique')


def validate_cidr(cidr):
    try:
        tok = cidr.split('/')
        if len(tok) != 2:
            raise configerror.ConfigError('Invalid cidr address %s' % cidr)
        validate_ipv4_address(tok[0])
    except Exception as exp:
        raise configerror.ConfigError(str(exp))

def validate_ip_in_network(ip, cidr):
    try:
        if netaddr.IPAddress(ip) not in netaddr.IPNetwork(cidr):
            raise configerror.ConfigError('%s does not belong to network %s' % (ip, cidr))
    except Exception as exp:
        raise configerror.ConfigError(str(exp))

def validate_keys_in_dictionary(keys, dictionary):
    for key in keys:
        if key not in dictionary:
            raise configerror.ConfigError('%s is not found' % key)

def validate_vlan(vlan):
    if vlan < 0 or vlan > 4096:
        raise configerror.ConfigError('Vlan %d is not valid' % vlan)

def get_own_hwmgmt_ip():
    try:
        #try both ipv4 and ipv6 addresses
        ips=[]
        output=subprocess.check_output(['sudo', 'ipmitool', 'lan', 'print'])
        lines = output.split('\n')
        for line in lines:
            if 'IP Address' in line and 'IP Address Source' not in line:
                data = line.split(':')
                if len(data) != 2:
                    raise configerror.ConfigError('Invalid hwmgmt ip configured')
                ip=data[1]
                import re
                ip=re.sub('[\s+]', '', ip)
                ips.append(ip)

        output_lan6=subprocess.check_output(['sudo', 'ipmitool', 'lan6', 'print'],stderr=subprocess.STDOUT)
        lines = output_lan6.split('\n')
        num_static_addr = 0
        num_dynamic_addr = 0
        #get max number of ipv6 static address
        for line in lines:
            if 'Static address max' in line:
                data = line.split(':')
                static_address = data[1]
                import re
                num_static_addr = int(re.sub('[\s+]', '', static_address))
            if 'Dynamic address max' in line:
                data = line.split(':')
                dynamic_address = data[1]
                import re
                num_dynamic_addr = int(re.sub('[\s+]', '', dynamic_address))

        for x in range(num_static_addr):
            address = 'IPv6 Static Address %s' %x
            for idx,val in enumerate(lines):
                if address in val:
                    if 'Address' in lines[idx+2]:
                        data=lines[idx+2].split(':',1)
                        ip=data[1]
                        import re
                        ip=re.sub('[\s+]', '', ip)
                        ip=ip.split('/',1)[0]
                        ips.append(ip.strip())

        for x in range(num_dynamic_addr):
            address = 'IPv6 Dynamic Address %s' %x
            for idx,val in enumerate(lines):
                if address in val:
                    if 'Address' in lines[idx+2]:
                        data=lines[idx+2].split(':',1)
                        ip=data[1]
                        import re
                        ip=re.sub('[\s+]', '', ip)
                        ip=ip.split('/',1)[0]
                        ips.append(ip.strip())
        return ips

    except Exception as exp:
        raise configerror.ConfigError(str(exp))

def is_virtualized():
    f=open('/proc/cpuinfo')
    lines = f.readlines()
    f.close()
    for line in lines:
        if line.startswith('flags') and 'hypervisor' in  line:
            return True
    return False

def get_installation_host_name(hostsconf):
    hostname = 'controller-1'
    if not is_virtualized():
        ownip = get_own_hwmgmt_ip()
        hostname = hostsconf.get_host_having_hwmgmt_address(ownip)
    return hostname

def flatten_config_data(jsondata):
    result = {}
    for key, value in jsondata.iteritems():
        try:
            result[key] = json.dumps(value)
        except Exception as exp:
            result[key] = value
    return result


def unflatten_config_data(props):
    propsjson = {}
    for name, value in props.iteritems():
        try:
            propsjson[name] = json.loads(value)
        except Exception as exp:
            propsjson[name] = value
    return propsjson

def add_lists(l1, l2):
    result = l1
    for v2 in l2:
        if v2 not in result:
            result.append(v2)
    return result
