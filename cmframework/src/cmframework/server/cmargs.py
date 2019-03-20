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
import sys
import argparse
import os

from ConfigParser import SafeConfigParser

from cmframework.apis import cmerror
from cmframework.utils import cmlogger


class CMArgsParser(object):
    def __init__(self, prog):
        self.prog = prog
        self.ip = None
        self.port = None
        self.verbose = False
        self.log_level = cmlogger.CMLogger.str_to_level('debug')
        self.log_dest = cmlogger.CMLogger.str_to_dest('syslog')
        self.disable_remote_activation = False
        self.rmq_host = None
        self.rmq_port = None
        self.activators = None
        self.validators = None
        self.rmq_ip = None
        self.backend_uri = None
        self.backend_api = None
        self.filename = None
        self.inventory_handlers = None
        self.inventory_data = None
        self.install_phase = False
        self.activationstate_handler_uri = None
        self.activationstate_handler_api = None
        self.activator_workers = 1
        self.snapshot_handler_uri = None
        self.snapshot_handler_api = None
        self.alarmhandler_api = None

    def parse(self, args):
        argparse.ArgumentParser(description='Configuration Management Server',
                                prog=self.prog)

        if '--file' in args:
            self.parse_config(args)
        else:
            self.parse_cmd_line(args)

    def parse_config(self, args):
        parser = argparse.ArgumentParser(description='Configuration Management Server',
                                         prog=self.prog)

        parser.add_argument('--file',
                            dest='filename',
                            required=True,
                            type=str,
                            action='store')
        try:
            args = parser.parse_args(args)
            self.filename = args.filename
        except Exception as error:
            raise cmerror.CMError(str(error))

        self.parse_config_file()

    def parse_config_file(self):
        config = SafeConfigParser(
            {'log_level': cmlogger.CMLogger.level_to_str(self.log_level),
             'log_dest': cmlogger.CMLogger.dest_to_str(self.log_dest),
             'verbose': repr(self.verbose),
             'disable_remote_activation': repr(self.disable_remote_activation),
             'activator_workers': '10',
             'alarmhandler_api': 'cmframework.lib.cmalarmhandler_dummy.AlarmHandler_Dummy',
             'snapshot_handler_api': ''})
        try:
            config.read(self.filename)
            self.ip = config.get('cmserver', 'ip')
            self.port = config.getint('cmserver', 'port')
            self.backend_api = config.get('cmserver', 'backend_api')
            self.backend_uri = config.get('cmserver', 'backend_uri')
            self.verbose = config.getboolean('cmserver', 'verbose')
            self.log_level = cmlogger.CMLogger.str_to_level(config.get('cmserver', 'log_level'))
            self.log_dest = cmlogger.CMLogger.str_to_dest(config.get('cmserver', 'log_dest'))
            self.validators = CMArgsParser.dir_parser(config.get('cmserver', 'validators'))
            self.activators = CMArgsParser.dir_parser(config.get('cmserver', 'activators'))
            self.disable_remote_activation = \
                config.getboolean('cmserver', 'disable_remote_activation')
            if not self.disable_remote_activation:
                self.rmq_ip = config.get('cmserver', 'rmq_ip')
                self.rmq_port = config.getint('cmserver', 'rmq_port')
            self.inventory_handlers = CMArgsParser.dir_parser(config.get('cmserver',
                                                                         'inventory_handlers'))
            self.inventory_data = config.get('cmserver', 'inventory_data')
            self.install_phase = config.getboolean('cmserver', 'install_phase')
            self.activationstate_handler_uri = config.get('cmserver', 'activationstate_handler_uri')
            self.activationstate_handler_api = config.get('cmserver', 'activationstate_handler_api')
            self.activator_workers = config.getint('cmserver', 'activator_workers')
            self.snapshot_handler_uri = config.get('cmserver', 'snapshot_handler_uri')
            self.snapshot_handler_api = config.get('cmserver', 'snapshot_handler_api')
            self.alarmhandler_api = config.get('cmserver', 'alarmhandler_api')
        except Exception as error:
            raise cmerror.CMError(str(error))

    def parse_cmd_line(self, args):
        parser = argparse.ArgumentParser(description='Configuration Management Server',
                                         prog=self.prog)

        parser.add_argument('--ip',
                            required=True,
                            help='The IP address to listen to',
                            type=str,
                            action='store')

        parser.add_argument('--port',
                            required=True,
                            help='The port number used for listening',
                            type=int,
                            action='store')

        parser.add_argument('--backend-api',
                            dest='backend_api',
                            metavar='BACKEND-API',
                            required=True,
                            help='The module.class implementing the backend api',
                            type=str,
                            action='store')

        parser.add_argument('--backend-uri',
                            dest='backend_uri',
                            metavar='BACKEND-URI',
                            required=True,
                            help='The uri needed by the backend api',
                            type=str, action='store')

        parser.add_argument('--log-level',
                            dest='log_level',
                            metavar='LOG-LEVEL',
                            required=False,
                            help=('The enabled logging level, possible values are '
                                  '{debug, info, warn, error}'),
                            type=CMArgsParser.log_level_parser,
                            default=self.log_level,
                            action='store')

        parser.add_argument('--log-dest',
                            dest='log_dest',
                            metavar='LOG-DEST',
                            required=False,
                            help='The logs destination, possible values are {console, syslog}',
                            type=CMArgsParser.log_dest_parser,
                            default=self.log_dest,
                            action='store')

        parser.add_argument('--verbose',
                            dest='verbose',
                            required=False,
                            default=self.verbose,
                            help='Enable verbose mode',
                            action='store_true')

        parser.add_argument('--validators',
                            dest='validators',
                            metavar='VALIDATORS-PATH',
                            required=True,
                            help='The full path were validatation plugin(s) are located',
                            type=CMArgsParser.dir_parser,
                            action='store')

        parser.add_argument('--activators',
                            dest='activators',
                            metavar='ACTIVATORS-PATH',
                            required=True,
                            help='The full path were activation plugin(s) are located',
                            type=CMArgsParser.dir_parser,
                            action='store')

        parser.add_argument('--disable-remote-activation',
                            dest='disable_remote_activation',
                            required=False,
                            default=self.disable_remote_activation,
                            help='Enable running activators in the target nodes',
                            action='store_true')

        parser.add_argument('--rmq-ip',
                            dest='rmq_ip',
                            metavar='RMQ-IP',
                            required=False,
                            help='RMQ broker IP address',
                            type=str,
                            action='store')

        parser.add_argument('--rmq-port',
                            dest='rmq_port',
                            metavar='RMQ-PORT',
                            required=False,
                            help='RMQ broker port number',
                            type=int,
                            action='store')

        parser.add_argument('--inventory-handlers',
                            dest='inventory_handlers',
                            metavar='INVENTORY-HANDLERS-PATH',
                            required=True,
                            help='The full path were inventory handlers are located',
                            type=CMArgsParser.dir_parser,
                            action='store')

        parser.add_argument('--inventory-data',
                            dest='inventory_data',
                            metavar='INVENTORY-DATA',
                            required=True,
                            help='The full path for the inventory data file',
                            type=str,
                            action='store')

        parser.add_argument('--install-phase',
                            dest='install_phase',
                            required=False,
                            default=False,
                            help='Indicate install phase startup',
                            action='store_true')

        parser.add_argument('--activationstate-handler-api',
                            dest='activationstate_handler_api',
                            metavar='ACTIVATIONSTATE-HANDLER-API',
                            required=True,
                            help='The module.class implementing the activationstate handler api',
                            type=str,
                            action='store')

        parser.add_argument('--activationstate-handler-uri',
                            dest='activationstate_handler_uri',
                            metavar='ACTIVATIONSTATE-HANDLER-URI',
                            required=True,
                            help='The uri needed by the activationstate handler uri',
                            type=str, action='store')

        parser.add_argument('--activator-workers',
                            dest='activator_workers',
                            metavar='ACTIVATOR_WORKERS',
                            required=False,
                            default=1,
                            help='Number of activator workers',
                            type=int,
                            action='store')

        parser.add_argument('--snapshot-handler-api',
                            dest='snapshot_handler_api',
                            metavar='SNAPSHOT-HANDLER-API',
                            required=True,
                            help='The module.class implementing the snapshot handler api',
                            type=str,
                            action='store')

        parser.add_argument('--snapshot-handler-uri',
                            dest='snapshot_handler_uri',
                            metavar='SNAPSHOT-HANDLER-URI',
                            required=False,
                            default='',
                            help='The uri needed by the snapshot handler uri',
                            type=str, action='store')

        parser.add_argument('--alarmhandler-api',
                            dest='alarmhandler_api',
                            metavar='ALARMHANDLER-API',
                            required=True,
                            help='The module.class implementing the alarmhandler api',
                            type=str,
                            action='store')

        try:
            args = parser.parse_args(args)
            self.ip = args.ip
            self.port = args.port
            self.backend_api = args.backend_api
            self.backend_uri = args.backend_uri
            self.verbose = args.verbose
            self.log_level = args.log_level
            self.log_dest = args.log_dest
            self.validators = args.validators
            self.activators = args.activators
            self.disable_remote_activation = args.disable_remote_activation
            if not self.disable_remote_activation:
                self.rmq_ip = args.rmq_ip
                self.rmq_port = args.rmq_port
            self.inventory_handlers = args.inventory_handlers
            self.inventory_data = args.inventory_data
            self.install_phase = args.install_phase
            self.activationstate_handler_api = args.activationstate_handler_api
            self.activationstate_handler_uri = args.activationstate_handler_uri
            self.activator_workers = args.activator_workers
            self.snapshot_handler_api = args.snapshot_handler_api
            self.snapshot_handler_uri = args.snapshot_handler_uri
            self.alarmhandler_api = args.alarmhandler_api
        except Exception as error:
            raise cmerror.CMError(str(error))

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

    @staticmethod
    def dir_parser(path):
        if os.path.isdir(path):
            return path
        raise argparse.ArgumentTypeError('Not a directory')

    def get_ip(self):
        return self.ip

    def get_port(self):
        return self.port

    def get_backend_api(self):
        return self.backend_api

    def get_backend_uri(self):
        return self.backend_uri

    def get_log_level(self):
        return self.log_level

    def get_log_dest(self):
        return self.log_dest

    def get_verbose(self):
        return self.verbose

    def get_validators(self):
        return self.validators

    def get_activators(self):
        return self.activators

    def get_disable_remote_activation(self):
        return self.disable_remote_activation

    def get_rmq_ip(self):
        return self.rmq_ip

    def get_rmq_port(self):
        return self.rmq_port

    def get_inventory_handlers(self):
        return self.inventory_handlers

    def get_inventory_data(self):
        return self.inventory_data

    def is_install_phase(self):
        return self.install_phase

    def get_activationstate_handler_api(self):
        return self.activationstate_handler_api

    def get_activationstate_handler_uri(self):
        return self.activationstate_handler_uri

    def get_activator_workers(self):
        return self.activator_workers

    def get_snapshot_handler_api(self):
        return self.snapshot_handler_api

    def get_snapshot_handler_uri(self):
        return self.snapshot_handler_uri

    def get_alarmhandler_api(self):
        return self.alarmhandler_api


def main():
    cm_parser = CMArgsParser('cmserver')
    try:
        cm_parser.parse(sys.argv[1:])
        print 'ip = %s' % cm_parser.get_ip()
        print 'port = %d' % cm_parser.get_port()
        print 'backend-api = %s' % cm_parser.get_backend_api()
        print 'backend-uri = %s' % cm_parser.get_backend_uri()
        print 'log-level = %s' % cmlogger.CMLogger.level_to_str(cm_parser.get_log_level())
        print 'log-dest = %s' % cmlogger.CMLogger.dest_to_str(cm_parser.get_log_dest())
        print 'verbose = %s' % repr(cm_parser.get_verbose())
        print 'validators = %s' % repr(cm_parser.get_validators())
        print 'activators = %s' % repr(cm_parser.get_activators())
        print 'rmq-ip = %s' % repr(cm_parser.get_rmq_ip())
        print 'rmq-port = %s' % repr(cm_parser.get_rmq_port())
        print 'inventory-handlers = %s' % repr(cm_parser.get_inventory_handlers())
        print 'inventory-data = %s' % repr(cm_parser.get_inventory_data())
        print 'install-phase = %s' % repr(cm_parser.is_install_phase())
        print 'activationstate-handler-api = %s' % repr(cm_parser.get_activationstate_handler_api())
        print 'activationstate-handler-uri = %s' % repr(cm_parser.get_activationstate_handler_uri())
        print 'activator-workers = %s' % repr(cm_parser.get_activator_workers())
        print 'snapshot-handler-api = %s' % repr(cm_parser.get_snapshot_handler_api())
        print 'snapshot-handler-uri = %s' % repr(cm_parser.get_snapshot_handler_uri())
        print 'alarmhandler-api = %s' % cm_parser.get_alarmhandler_api()
    except cmerror.CMError as error:
        print 'Got error %s' % str(error)
        sys.exit(1)


if __name__ == '__main__':
    main()
