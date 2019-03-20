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

import eventlet  # noqa
from eventlet import wsgi  # noqa
eventlet.monkey_patch()  # noqa
import os
import json
import sys
import logging
import traceback

import ConfigParser
from cmframework.utils import cmbackendpluginclient
from cmframework.utils import cmlogger
from cmframework.utils import cmbackendhandler
from cmframework.utils import cmactivationstatehandler
from cmframework.utils import cmalarmhandler
from cmframework.utils import cmsnapshothandler
from cmframework.server import cmargs
from cmframework.server import cmprocessor
from cmframework.server import cmrestapifactory
from cmframework.server import cmwsgihandler
from cmframework.server import cmvalidator
from cmframework.server import cmactivator
from cmframework.server import cmactivateserverhandler
from cmframework.server import cmchangemonitor
from cmframework.utils.cmansibleinventory import AnsibleInventory


def main():
    try:
        # parse the arguments
        parser = cmargs.CMArgsParser('cmserver')
        parser.parse(sys.argv[1:])

        # Read configuration names which should be masked in logging
        mask_names = _read_maskable_names()

        # initialize the logger
        _ = cmlogger.CMLogger(parser.get_log_dest(),
                              parser.get_verbose(),
                              parser.get_log_level(),
                              mask_names)

        logging.info('CM server is starting up')

        # initialize the change monitor object
        changemonitor = cmchangemonitor.CMChangeMonitor()

        # load backend plugin
        logging.info('Initializing backend handler')
        backend_args = {}
        backend_args['uri'] = parser.get_backend_uri()
        backend = cmbackendhandler.CMBackendHandler(parser.get_backend_api(), **backend_args)

        # construct the plugin client library
        logging.info('Initialize plugin client library')
        plugin_client = cmbackendpluginclient.CMBackendPluginClient(parser.get_backend_api(),
                                                                    **backend_args)

        # load activation state handler
        logging.info('Initializing activation state handler')
        activationstatehandler_args = {}
        activationstatehandler_args['uri'] = parser.get_activationstate_handler_uri()
        activationstate_handler = cmactivationstatehandler.CMActivationStateHandler(
            parser.get_activationstate_handler_api(), **activationstatehandler_args)

        # initialize validator
        logging.info('Initializing validator')
        validator = cmvalidator.CMValidator(parser.get_validators(), plugin_client)

        # initializing activation handling process
        logging.info('Initializing activator')
        activator = cmactivator.CMActivator(parser.get_activator_workers())

        # initialize activator rmq handler
        if not parser.get_disable_remote_activation():
            from cmframework.server import cmactivatermqhandler
            logging.info('Initializing activator rmq handler')
            activatermqhandler = cmactivatermqhandler.CMActivateRMQHandler(parser.get_rmq_ip(),
                                                                           parser.get_rmq_port())
            activator.add_handler(activatermqhandler)

        # initialize activator server handler
        logging.info('Initializing activator server handler')
        activateserverhandler = cmactivateserverhandler.CMActivateServerHandler(
            parser.get_activators(), plugin_client, changemonitor, activationstate_handler)
        activator.add_handler(activateserverhandler)

        # starting activator
        logging.info('Starting activation handling process')
        activator.start()

        # start alarm handler
        logging.info('Starting alarm handler process')
        alarmhandler = cmalarmhandler.AlarmHandler()
        alarmhandler.set_library_impl(parser.get_alarmhandler_api())
        alarmhandler.start()

        # load snapshot handler
        logging.info('Initializing snapshot handler')
        snapshothandler_args = {}
        snapshothandler_args['uri'] = parser.get_snapshot_handler_uri()
        snapshot_handler = cmsnapshothandler.CMSnapshotHandler(
            parser.get_snapshot_handler_api(), **snapshothandler_args)

        # initialize processor
        logging.info('Initializing CM processor')
        processor = cmprocessor.CMProcessor(backend,
                                            validator,
                                            activator,
                                            changemonitor,
                                            activationstate_handler,
                                            snapshot_handler)

        if not parser.is_install_phase():
            # generate inventory file
            logging.info('Generate inventory file')
            properties = backend.get_properties('.*')
            inventory = AnsibleInventory(properties, parser.get_inventory_handlers())
            inventory_data = inventory.generate_inventory()
            with open(parser.get_inventory_data(), 'w') as inventory_file:
                inventory_file.write(json.dumps(inventory_data, indent=4, sort_keys=True))

            # publish full activate request to on-line activators
            logging.info('Ask on-line activators to full translate')
            processor.activate(startup_activation=True)

            # remove inventory file
            logging.info('Remove inventory file')
            try:
                os.remove(parser.get_inventory_data())
            except OSError:
                pass

        # initialize rest api factory
        logging.info('Initializing REST API factory')
        base_url = 'http://' + parser.get_ip() + ':' + \
                   str(parser.get_port()) + '/cm/'
        rest_api_factory = cmrestapifactory.CMRestAPIFactory(processor, base_url)

        # initialize wsgi handler
        logging.info('Initializing the WSGI handler')
        wsgihandler = cmwsgihandler.CMWSGIHandler(rest_api_factory)

        # start the http server
        logging.info('Start listening to http requests')
        wsgi.server(eventlet.listen((parser.get_ip(), parser.get_port())), wsgihandler)
    except KeyboardInterrupt as exp:
        logging.info('CM server shutting down')
        return 0
    except Exception as exp:  # pylint: disable=broad-except
        logging.error('Got exception %s', str(exp))
        traceback.print_exc()
        return 1


def _read_maskable_names():
    MASK_DIR = '/etc/cmframework/masks.d/'
    all_names = []
    filenames = [MASK_DIR + f for f in os.listdir(MASK_DIR)]
    for filename in filenames:
        config = ConfigParser.SafeConfigParser()
        config.read(filename)
        names = json.loads(config.get('Passwords', 'names'))
        all_names.extend(names)
    return all_names


if __name__ == "__main__":
    sys.exit(main())
