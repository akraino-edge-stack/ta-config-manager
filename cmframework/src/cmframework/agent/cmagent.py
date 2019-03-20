#! /usr/bin/python

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
import sys
import argparse
import socket
import logging
import subprocess

from cmframework.apis import cmmanage
from cmframework.apis import cmerror
from cmframework.utils import cmlogger
from cmframework.utils import cmalarm


class VerboseLogger(object):
    def __call__(self, msg):
        print (msg)


class CMAgent(object):
    def __init__(self):
        self.prog = 'cmagent'
        self.ip = None
        self.port = None
        self.verbose = False
        self.log_level = cmlogger.CMLogger.str_to_level('debug')
        self.log_dest = cmlogger.CMLogger.str_to_dest('syslog')
        self.api = None
        self.verbose_logger = VerboseLogger()

    @staticmethod
    def log_level_parser(level):
        try:
            return cmlogger.CMLogger.str_to_level(level)
        except cmerror.CMError as exp:
            raise argparse.ArgumentTypeError(str(exp))

    @staticmethod
    def log_dest_parser(dest):
        try:
            return cmlogger.CMLogger.str_to_dest(dest)
        except cmerror.CMError as exp:
            raise argparse.ArgumentTypeError(str(exp))

    def __call__(self, args):
        parser = argparse.ArgumentParser(description='Configuration Management Agent',
                                         prog=self.prog)
        parser.add_argument('--ip',
                            dest='ip',
                            metavar='SERVER-IP',
                            default='config-manager',
                            type=str,
                            action='store')

        parser.add_argument('--port',
                            dest='port',
                            metavar='SERVER-PORT',
                            default=61100,
                            type=int,
                            action='store')

        parser.add_argument('--client-lib',
                            dest='client_lib',
                            metavar='CLIENT-LIB',
                            default='cmframework.lib.CMClientImpl',
                            type=str,
                            action='store')

        parser.add_argument('--log-level',
                            dest='log_level',
                            metavar='LOG-LEVEL',
                            required=False,
                            help=('The enabled logging level, possible values are '
                                  '{debug, info, warn, error}'),
                            type=CMAgent.log_level_parser,
                            default=self.log_level,
                            action='store')

        parser.add_argument('--log-dest',
                            dest='log_dest',
                            metavar='LOG-DEST',
                            required=False,
                            help='The logs destination, possible values are {console, syslog}',
                            type=CMAgent.log_dest_parser,
                            default=self.log_dest,
                            action='store')

        parser.add_argument('--verbose',
                            required=False,
                            default=False,
                            action='store_true')

        args = parser.parse_args(args)

        self.process(args)

    def _init_api(self, ip, port, client_lib):
        try:
            serverip = socket.gethostbyname(ip)
        except socket.gaierror:
            # use localhost in-case we cannot resolve the provided hostname
            serverip = '127.0.0.1'

        self.api = cmmanage.CMManage(serverip, port, client_lib, self.verbose_logger)

    @staticmethod
    def _reboot_node():
        cmd = 'systemctl reboot'
        args = cmd.split()
        process = subprocess.Popen(args)
        return process.wait()

    def process(self, args):
        cmlogger.CMLogger(args.log_dest, args.verbose, args.log_level)

        self._init_api(args.ip, args.port, args.client_lib)

        node_name = socket.gethostname()

        reboot_request_alarm = cmalarm.CMRebootRequestAlarm()
        reboot_request_alarm.cancel_alarm_for_node(node_name)

        reboot = self.api.activate_node(node_name)
        if reboot:
            logging.warn('Going to reboot this node')
            res = self._reboot_node()
            if res != 0:
                logging.error('Reboot failed')


def main():
    try:
        agent = CMAgent()
        args = sys.argv[1:]
        agent(args)
    except cmerror.CMError as exp:
        print ('Failed with error: %s' % str(exp))
        return 1
    # TODO: catch all exceptions?


if __name__ == '__main__':
    sys.exit(main())
