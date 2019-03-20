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
import inspect
import socket
import pprint
import prettytable

from cmframework.apis import cmmanage
from cmframework.apis import cmerror


class VerboseLogger(object):
    def __call__(self, msg):
        print(msg)


class CMCLIHandler(object):
    def __init__(self):
        self.api = None
        self.verbose_logger = VerboseLogger()

    def _init_api(self, ip, port, client_lib, verbose):
        logger = None
        if verbose:
            logger = self.verbose_logger

        try:
            serverip = socket.gethostbyname(ip)
        except Exception:  # pylint: disable=broad-except
            # use localhost in-case we cannot resolve the provided hostname
            serverip = '127.0.0.1'

        self.api = cmmanage.CMManage(serverip, port, client_lib, logger)

    def set_handler(self, subparser):
        subparser.set_defaults(handler=self)

    # pylint: disable=no-self-use, unused-argument
    def init_subparser(self, subparsers):
        raise cmerror.CMError('Not implemented')

    # pylint: disable=no-self-use, unused-argument
    def __call__(self, args):
        raise cmerror.CMError('Not implemented')


class CMCLIGetPropertyHandler(CMCLIHandler):
    def init_subparser(self, subparsers):
        subparser = subparsers.add_parser('get-property', help='Get a property value')
        subparser.add_argument('--property',
                               required=True,
                               dest='name',
                               metavar='NAME',
                               action='store')
        subparser.add_argument('--snapshot',
                               required=False,
                               dest='snapshot',
                               metavar='SNAPSHOT-NAME',
                               action='store')
        self.set_handler(subparser)

    def __call__(self, args):
        self._init_api(args.ip, args.port, args.client_lib, args.verbose)
        name = args.name
        snapshot = args.snapshot
        value = self.api.get_property(name, snapshot)
        print(value)


class CMCLIGetPropertiesHandler(CMCLIHandler):
    def init_subparser(self, subparsers):
        subparser = subparsers.add_parser('get-properties',
                                          help='Get the properties matching a filter')
        subparser.add_argument('--matching-filter',
                               required=True,
                               dest='matching_filter',
                               metavar='MATCHING-FILTER',
                               action='store')
        subparser.add_argument('--snapshot',
                               required=False,
                               dest='snapshot',
                               metavar='SNAPSHOT-NAME',
                               action='store')
        self.set_handler(subparser)

    def __call__(self, args):
        self._init_api(args.ip, args.port, args.client_lib, args.verbose)
        matching_filter = args.matching_filter
        snapshot = args.snapshot
        props = self.api.get_properties(matching_filter, snapshot)
        for name, value in props.iteritems():
            print('%s=%s' % (name, value))


class CMCLISetPropertyHandler(CMCLIHandler):
    def init_subparser(self, subparsers):
        subparser = subparsers.add_parser('set-property', help='Set a property')
        subparser.add_argument('--property',
                               required=True,
                               dest='prop',
                               metavar='NAME VALUE',
                               action='store',
                               nargs=2)
        self.set_handler(subparser)

    def __call__(self, args):
        self._init_api(args.ip, args.port, args.client_lib, args.verbose)
        prop = args.prop
        change_uuid = self.api.set_property(prop[0], prop[1])
        print("change-uuid:%s" % change_uuid)


class CMCLISetPropertiesHandler(CMCLIHandler):
    def init_subparser(self, subparsers):
        subparser = subparsers.add_parser('set-properties', help='Set a group of properties')
        subparser.add_argument('--property',
                               required=True,
                               dest='props',
                               metavar='NAME VALUE',
                               action='append',
                               nargs=2)
        self.set_handler(subparser)

    def __call__(self, args):
        self._init_api(args.ip, args.port, args.client_lib, args.verbose)
        props = args.props
        dic = {}
        for prop in props:
            name = prop[0]
            value = prop[1]
            dic[name] = value
        change_uuid = self.api.set_properties(dic)
        print("change-uuid:%s" % change_uuid)


class CMCLIDeletePropertyHandler(CMCLIHandler):
    def init_subparser(self, subparsers):
        subparser = subparsers.add_parser('delete-property', help='Delete a property')
        subparser.add_argument('--property',
                               required=True,
                               dest='name',
                               metavar='NAME',
                               action='store')
        self.set_handler(subparser)

    def __call__(self, args):
        self._init_api(args.ip, args.port, args.client_lib, args.verbose)
        name = args.name
        change_uuid = self.api.delete_property(name)
        print("change-uuid:%s" % change_uuid)


class CMCLIDeletePropertiesWithFilterHandler(CMCLIHandler):
    def init_subparser(self, subparsers):
        subparser = subparsers.add_parser('delete-properties-with-filter',
                                          help='Delete properties matching a filter')
        subparser.add_argument('--matching-filter',
                               required=True,
                               dest='matching_filter',
                               metavar='MATCHING-FILTER',
                               action='store')
        self.set_handler(subparser)

    def __call__(self, args):
        self._init_api(args.ip, args.port, args.client_lib, args.verbose)
        matching_filter = args.matching_filter
        change_uuid = self.api.delete_properties(matching_filter)
        print("change-uuid:%s" % change_uuid)


class CMCLIDeletePropertiesHandler(CMCLIHandler):
    def init_subparser(self, subparsers):
        subparser = subparsers.add_parser('delete-properties', help='Delete a group of properties')
        subparser.add_argument('--property',
                               required=True,
                               dest='props',
                               metavar='PROPERY-NAME',
                               action='append')
        self.set_handler(subparser)

    def __call__(self, args):
        self._init_api(args.ip, args.port, args.client_lib, args.verbose)
        props = args.props
        change_uuid = self.api.delete_properties(props)
        print("change-uuid:%s" % change_uuid)


class CMCLICreateSnapshotHandler(CMCLIHandler):
    def init_subparser(self, subparsers):
        subparser = subparsers.add_parser('create-snapshot',
                                          help='Take a snapshot of the configuration data')
        subparser.add_argument('--name',
                               required=True,
                               dest='snapshot_full_name',
                               metavar='SNAPSHOT-FULL-NAME',
                               action='store')
        self.set_handler(subparser)

    def __call__(self, args):
        self._init_api(args.ip, args.port, args.client_lib, args.verbose)
        snapshot = args.snapshot_full_name
        self.api.create_snapshot(snapshot)


class CMCLIRestoreSnapshotHandler(CMCLIHandler):
    def init_subparser(self, subparsers):
        subparser = subparsers.add_parser('restore-snapshot',
                                          help='Restore a configuration snapshot')
        subparser.add_argument('--name',
                               required=True,
                               dest='snapshot_full_name',
                               metavar='SNAPSHOT-FULL-NAME',
                               action='store')
        self.set_handler(subparser)

    def __call__(self, args):
        self._init_api(args.ip, args.port, args.client_lib, args.verbose)
        snapshot = args.snapshot_full_name
        self.api.restore_snapshot(snapshot)


class CMCLIDeleteSnapshotHandler(CMCLIHandler):
    def init_subparser(self, subparsers):
        subparser = subparsers.add_parser('delete-snapshot', help='Delete a configuration snapshot')
        subparser.add_argument('--name',
                               required=True,
                               dest='snapshot_full_name',
                               metavar='SNAPSHOT-FULL-NAME',
                               action='store')
        self.set_handler(subparser)

    def __call__(self, args):
        self._init_api(args.ip, args.port, args.client_lib, args.verbose)
        snapshot = args.snapshot_full_name
        self.api.delete_snapshot(snapshot)


class CMCLIListSnapshotHandler(CMCLIHandler):
    def init_subparser(self, subparsers):
        subparser = subparsers.add_parser('list-snapshots', help='List all configuration snapshots')
        self.set_handler(subparser)

    def __call__(self, args):
        self._init_api(args.ip, args.port, args.client_lib, args.verbose)
        snapshots = self.api.list_snapshots()
        sorted_snapshots = sorted(snapshots, key=lambda k: k['creation_date'])

        t = prettytable.PrettyTable(['Name', 'Date', 'Release', 'Build'])
        t.set_style(prettytable.PLAIN_COLUMNS)
        t.align = 'l'
        for snapshot in sorted_snapshots:
            t.add_row([snapshot['name'],
                       snapshot['creation_date'],
                       snapshot['release'],
                       snapshot['build']])
        print(t)


class CMCLIActivateHandler(CMCLIHandler):
    def init_subparser(self, subparsers):
        subparser = subparsers.add_parser(
            'activate',
            help='Activate the configuration in all or specified node')
        subparser.add_argument('--node-name',
                               required=False,
                               dest='node_name',
                               metavar='NODE-NAME',
                               action='store')
        self.set_handler(subparser)

    def __call__(self, args):
        self._init_api(args.ip, args.port, args.client_lib, args.verbose)
        node_name = args.node_name
        self.api.activate(node_name)


class CMCLIRebootHandler(CMCLIHandler):
    def init_subparser(self, subparsers):
        subparser = subparsers.add_parser('reboot-request',
                                          help=('Request reboot of a specified node '
                                                'during activation'))
        subparser.add_argument('--node-name',
                               required=True,
                               dest='node_name',
                               metavar='NODE-NAME',
                               action='store')
        self.set_handler(subparser)

    def __call__(self, args):
        self._init_api(args.ip, args.port, args.client_lib, args.verbose)
        node_name = args.node_name
        self.api.reboot_node(node_name)


class CMCLIBootstrapHandler(CMCLIHandler):
    def init_subparser(self, subparsers):
        subparser = subparsers.add_parser('bootstrap',
                                          help='Bootsrap the backend with the user config data')
        subparser.add_argument('--config',
                               required=True,
                               dest='config',
                               metavar='INITIAL-USER-CONFIG',
                               action='store')
        subparser.add_argument('--plugin_path',
                               required=True,
                               dest='plugin_path',
                               metavar='BOOTSTRAP-PLUGIN-PATH',
                               action='store')
        self.set_handler(subparser)

    def __call__(self, args):
        self._init_api(args.ip, args.port, args.client_lib, args.verbose)
        from cmframework.utils.cmuserconfig import UserConfig
        uc = UserConfig(args.config, args.plugin_path)
        flat_config = uc.get_flat_config()
        self.api.set_properties(flat_config)


class CMCLIAnsibleInventoryHandler(CMCLIHandler):
    def init_subparser(self, subparsers):
        subparser = subparsers.add_parser('ansible-inventory',
                                          help='Prints the ansible inventory json to output')
        subparser.add_argument('--plugin_path',
                               required=False,
                               default='/opt/cmframework/inventoryhandlers',
                               dest='plugin_path',
                               metavar='INVENTORY-HANDLERS-PLUGIN-PATH',
                               action='store')
        self.set_handler(subparser)

    def __call__(self, args):
        self._init_api(args.ip, args.port, args.client_lib, args.verbose)
        from cmframework.utils.cmansibleinventory import AnsibleInventory
        import json

        properties = self.api.get_properties('.*')

        inventory = AnsibleInventory(properties, args.plugin_path)
        inv = inventory.generate_inventory()

        print (json.dumps(inv, indent=4, sort_keys=True))


class CMAnsiblePlaybookHandler(CMCLIHandler):
    def init_subparser(self, subparsers):
        subparser = subparsers.add_parser('ansible-playbooks-generate',
                                          help=('Generate the ansible playbooks for the '
                                                'bootstrapping, provisioning, '
                                                'postconfig and finalizing phases'))
        subparser.add_argument('--bootstrapping-playbooks-path',
                               required=False,
                               default='/etc/lcm/playbooks/installation/bootstrapping',
                               dest='bootstrapping_path',
                               metavar='BOOTSTRAPPING-PLAYBOOKS-PATH',
                               action='store')
        subparser.add_argument('--provisioning-playbooks-path',
                               required=False,
                               default='/etc/lcm/playbooks/installation/provisioning',
                               dest='provisioning_path',
                               metavar='PROVISIONING-PLAYBOOKS-PATH',
                               action='store')
        subparser.add_argument('--postconfig-playbooks-path',
                               required=False,
                               default='/etc/lcm/playbooks/installation/postconfig',
                               dest='postconfig_path',
                               metavar='POSTCONFIG-PLAYBOOKS-PATH',
                               action='store')
        subparser.add_argument('--finalize-playbooks-path',
                               required=False,
                               default='/etc/lcm/playbooks/installation/finalize',
                               dest='finalize_path',
                               metavar='FINALIZE-PLAYBOOKS-PATH',
                               action='store')
        subparser.add_argument('--destination-path',
                               required=False,
                               default='/opt/openstack-ansible/playbooks/',
                               dest='destination_path',
                               metavar='DESTINATION-PATH',
                               action='store')
        self.set_handler(subparser)

    def __call__(self, args):
        from cmframework.utils.cmansibleplaybooks import AnsiblePlaybooks

        playbooks = AnsiblePlaybooks(args.destination_path, args.bootstrapping_path,
                                     args.provisioning_path, args.postconfig_path,
                                     args.finalize_path)
        playbooks.generate_playbooks()


class CMCLIDisableAutomaticActivationHandler(CMCLIHandler):
    def init_subparser(self, subparsers):
        subparser = subparsers.add_parser('disable-automatic-activation',
                                          help='Disable automatic activation')
        self.set_handler(subparser)

    def __call__(self, args):
        self._init_api(args.ip, args.port, args.client_lib, args.verbose)
        self.api.disable_automatic_activation()


class CMCLIEnableAutomaticActivationHandler(CMCLIHandler):
    def init_subparser(self, subparsers):
        subparser = subparsers.add_parser('enable-automatic-activation',
                                          help='Enable automatic activation')
        self.set_handler(subparser)

    def __call__(self, args):
        self._init_api(args.ip, args.port, args.client_lib, args.verbose)
        self.api.enable_automatic_activation()


class CMCLIGetChangesStatesHandler(CMCLIHandler):
    def init_subparser(self, subparsers):
        subparser = subparsers.add_parser('get-changes-states',
                                          help='Get the configuration changes states')
        subparser.add_argument('--uuid',
                               required=False,
                               dest='change_uuid',
                               metavar='CHANGE_UUID',
                               action='store')
        self.set_handler(subparser)

    def __call__(self, args):
        self._init_api(args.ip, args.port, args.client_lib, args.verbose)
        change_uuid = None
        if args.change_uuid:
            change_uuid = args.change_uuid

        result = self.api.get_changes_states(change_uuid)
        pp = pprint.PrettyPrinter(indent=4)
        pp.pprint(result)


def get_handlers_list():
    handlers = []
    for name, obj in inspect.getmembers(sys.modules[__name__]):
        if inspect.isclass(obj):
            if name != 'CMCLIHandler':
                if issubclass(obj, CMCLIHandler):
                    handlers.append(obj())
    return handlers


def main():
    handlers = get_handlers_list()
    for handler in handlers:
        print('handler is ', handler)


if __name__ == '__main__':
    main()
