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
import json
import os
import re

from cmdatahandlers.api.configmanager import ConfigManager
from cmframework.apis import cmmanage

from cliff import command
from cliff.show import ShowOne
from cliff.lister import Lister
from cliff.formatters.table import TableFormatter



class VerboseLogger(object):
    def __init__(self, logger):
        self.logger = logger

    def __call__(self, msg):
        self.logger.debug(msg)


def _add_basic_arguments(parser):
    parser.add_argument('--cmserver-ip',
                        dest='cmserverip',
                        metavar='IP',
                        required=False,
                        default='config-manager',
                        type=str,
                        action='store')
    parser.add_argument('--cmserver-port',
                        dest='cmserverport',
                        metavar='PORT',
                        required=False,
                        default=61100,
                        type=str,
                        action='store')
    parser.add_argument('--client-lib',
                        dest='clientlib',
                        metavar='LIB',
                        required=False,
                        default='cmframework.lib.CMClientImpl',
                        type=str,
                        action='store')


class ShowProperty(ShowOne):
    """A command for showing the value associated with a property"""

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(ShowProperty, self).get_parser(prog_name)
        _add_basic_arguments(parser)
        parser.add_argument(
            'property',
            metavar='<property>',
            help=('Property name'),
        )

        return parser

    @staticmethod
    def dumps(data):
        return json.dumps(data, sort_keys=True, indent=4, separators=(',', ':'))

    def take_action(self, parsed_args):
        try:
            logger = VerboseLogger(self.log)

            api = cmmanage.CMManage(parsed_args.cmserverip,
                                    parsed_args.cmserverport,
                                    parsed_args.clientlib,
                                    logger)

            cm_property = parsed_args.property

            data = api.get_properties('')

            d = {}
            for name, value in data.iteritems():
                try:
                    d[name] = json.loads(value)
                except Exception as ex:
                    d[name] = value

            cm = ConfigManager(d)
            cm.mask_sensitive_data()

            prop = d.get(cm_property)
            split = None
            if not prop:
                split = cm_property.split('.')
                cm_property = '.'.join(split[:2])
                prop = d.get(cm_property)

            if prop == '' or prop == None:
                raise Exception('{} not configured'.format(cm_property))

            d = d[cm_property]
            if split:
                if split[2:]:
                    for field in split[2:]:
                        try:
                            d = d[field]
                        except KeyError as ex:
                            raise Exception('{} not found in {}'.format(field, cm_property))

            if isinstance(d, dict):
                columns = tuple(d.keys())
                if isinstance(self.formatter, TableFormatter):
                    data = tuple(map(ShowProperty.dumps, d.values()))
                else:
                    data = tuple(d.values())
            else:
                columns = (parsed_args.property, )
                data = (d, )
            return (columns, data)

        except Exception:
            raise


class ListProperties(Lister):
    """A command for showing properties matching some filter"""

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(ListProperties, self).get_parser(prog_name)
        _add_basic_arguments(parser)
        parser.add_argument('--matching-filter',
                            dest='filter',
                            metavar='FILTER',
                            required=False,
                            default='.*',
                            type=str,
                            action='store')

        return parser

    def take_action(self, parsed_args):
        try:
            logger = VerboseLogger(self.log)

            api = cmmanage.CMManage(parsed_args.cmserverip,
                                    parsed_args.cmserverport,
                                    parsed_args.clientlib,
                                    logger)

            prop_filter = parsed_args.filter
            data = api.get_properties('')

            header = ('property', 'value')

            columns = ()

            d = {}
            for name, value in data.iteritems():
                try:
                    d[name] = json.loads(value)
                except Exception as ex:
                    d[name] = value

            cm = ConfigManager(d)
            cm.mask_sensitive_data()

            pattern = re.compile(prop_filter)
            for name, value in d.iteritems():
                if not pattern.match(name):
                    continue
                if isinstance(self.formatter, TableFormatter):
                    try:
                        v = json.dumps(value, sort_keys=True, indent=1, separators=(',', ':'))
                    except Exception:
                        pass
                else:
                    v = value
                entry = (name, v)
                columns = (entry,) + columns
            if not columns:
                raise Exception('Not found')

            return (header, columns)

        except Exception:
            raise


class DeleteProperty(command.Command):
    """A command for deleting a property"""

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(DeleteProperty, self).get_parser(prog_name)
        _add_basic_arguments(parser)

        parser.add_argument(
            'property',
            metavar='<property>',
            help=('Property name'),
        )

        return parser

    def take_action(self, parsed_args):
        try:
            logger = VerboseLogger(self.log)

            api = cmmanage.CMManage(parsed_args.cmserverip,
                                    parsed_args.cmserverport,
                                    parsed_args.clientlib,
                                    logger)


            api.delete_property(parsed_args.property)


            self.app.stdout.write('%s deleted successfully\n' % parsed_args.property)

        except Exception as exp:
            self.app.stderr.write('Failed with error %s\n' % str(exp))


class SetProperty(command.Command):
    """A command for setting a property"""

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(SetProperty, self).get_parser(prog_name)
        _add_basic_arguments(parser)

        parser.add_argument(
            'property',
            metavar='<property>',
            help=('Property name'),
        )

        parser.add_argument('--value',
                            dest='value',
                            metavar='VALUE',
                            required=False,
                            type=str,
                            action='store')

        parser.add_argument('--file',
                            dest='file',
                            metavar='FILE',
                            required=False,
                            type=str,
                            action='store')
        return parser

    def take_action(self, parsed_args):
        try:
            logger = VerboseLogger(self.log)

            api = cmmanage.CMManage(parsed_args.cmserverip,
                                    parsed_args.cmserverport,
                                    parsed_args.clientlib,
                                    logger)

            if parsed_args.value and parsed_args.file:
                raise Exception('Either --value or --file needs to be specified')

            if parsed_args.value:
                api.set_property(parsed_args.property, parsed_args.value)
            elif parsed_args.file:
                if not os.path.exists(parsed_args.file):
                    raise Exception('File %s is not valid' % parsed_args.file)

                with open(parsed_args.file, 'r') as f:
                    data = ""
                    try:
                        data = f.read()
                        d = json.loads(data)
                        data = json.dumps(d)
                    except Exception as exp:
                        pass

                    api.set_property(parsed_args.property, data)
            else:
                raise Exception('--value or --file needs to be specified')


            self.app.stdout.write('%s set successfully\n' % parsed_args.property)

        except Exception as exp:
            self.app.stderr.write('Failed with error %s\n' % str(exp))


class DumpPropertyToFile(command.Command):
    """A command for dumping property value to a file"""

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(DumpPropertyToFile, self).get_parser(prog_name)
        _add_basic_arguments(parser)

        parser.add_argument(
            'property',
            metavar='<property>',
            help=('Property name'),
        )

        parser.add_argument(
            'file',
            metavar='<FILE>',
            help=('Filename'),
        )

        return parser

    def take_action(self, parsed_args):
        try:
            logger = VerboseLogger(self.log)

            api = cmmanage.CMManage(parsed_args.cmserverip,
                                    parsed_args.cmserverport,
                                    parsed_args.clientlib,
                                    logger)

            cm_property = parsed_args.property
            config = api.get_properties('')

            if os.path.exists(parsed_args.file):
                raise Exception('File %s already exists' % parsed_args.file)

            with open(parsed_args.file, 'w') as f:
                d = {}
                if cm_property not in config.keys():
                    raise Exception('Property not found')
                for name, value in config.iteritems():
                    try:
                        d[name] = json.loads(value)
                    except Exception as ex:
                        d[name] = value
                cm = ConfigManager(d)
                cm.mask_sensitive_data()
                d = d.get(cm_property)
                try:
                    data = json.dumps(d, sort_keys=True, indent=1, separators=(',', ':'))
                except Exception as exp:
                    data = d
                if data == 'null' or data == '""':
                    data = ''
                f.write(data)

            self.app.stdout.write('Completed successfully\n')

        except Exception as exp:
            self.app.stderr.write('Failed with error %s\n' % str(exp))
