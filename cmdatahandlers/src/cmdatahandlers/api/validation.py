#!/usr/bin/python2

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

import logging
import re

from netaddr import IPAddress
from netaddr import IPNetwork
from netaddr import IPRange
from netaddr import AddrFormatError

from cmdatahandlers.api import configerror


class ValidationError(configerror.ConfigError):
    def __init__(self, description):
        configerror.ConfigError.__init__(self, ' Validation error: %s' % description)



class ValidationUtils:

    def validate_ip_address(self, addr):
        try:
            IPAddress(addr)
        except AddrFormatError as exc:
            raise ValidationError("Invalid ip address: {0}".format(exc))


    def validate_subnet_address(self, cidr):
        try:
            net = IPNetwork(cidr)
        except AddrFormatError as exc:
            raise ValidationError('Invalid subnet address: {0}'.format(exc))
        #it seems ipnetwork compress ipv6 cidr.
        #skip this for ipv6
        if net.version == 4:
            if cidr != str(net.cidr):
               raise ValidationError('Given CIDR %s is not equal to network CIDR %s'
                                  % (cidr, str(net.cidr)))


    def validate_ip_range(self, start_ip, end_ip):
        try:
            IPRange(start_ip, end_ip)
        except AddrFormatError as exc:
            raise ValidationError('Invalid ip range: {0}'.format(exc))


    def validate_ip_in_subnet(self, ip_addr, cidr):
        self.validate_ip_address(ip_addr)
        ip = IPAddress(ip_addr)

        self.validate_subnet_address(cidr)
        subnet = IPNetwork(cidr)
        if not ip in subnet or ip == subnet.ip  or ip == subnet.broadcast:
            raise ValidationError('IP %s is not a valid address in subnet %s' % (ip_addr, cidr))


    def validate_ip_in_range(self, addr, start, end):
        self.validate_ip_address(addr)
        self.validate_ip_range(start, end)
        if IPAddress(addr) not in IPRange(start, end):
            raise ValidationError('IP %s is not in range %s - %s' % (addr, start, end))


    def validate_ip_not_in_range(self, addr, start, end):
        self.validate_ip_address(addr)
        self.validate_ip_range(start, end)
        if IPAddress(addr) in IPRange(start, end):
            raise ValidationError('IP %s is in reserved range %s - %s' % (addr, start, end))


    def validate_username(self, user):
        if not re.match('^[a-zA-Z][\da-zA-Z-_]+[\da-zA-Z]$', user):
            raise ValidationError('Invalid user name %s' % user)
