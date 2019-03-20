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
from cmframework.apis import cmclient


class CMManage(cmclient.CMClient):
    """
        Usage Example:
            class VerboseLogger:
                def __call__(self, msg):
                    print(msg)

            logger = VerboseLogger()

            client = CMManage(192.128.254.10, 51110, cmclient.CMClientImpl, logger)
            try:
                value = client.create_snapshot('snapshot1')
            except cmapis.cmerror.CMError as error:
                print('Got exception %s' % str(error))
    """

    def __init__(self, server_ip='config-manager', server_port=61100,
                 client_impl_module='cmframework.lib.CMClientImpl', verbose_logger=None):
        """ initialize the client interface

            Arguments:

            server_ip:  The configuration management server ip address.

            server_port: The configuration management server port number.

            client_lib_impl_module: The module implementing the client library.

            verbose_logger: The verbose logging callable. any callable which
                            takes a string as input argument can be used.

            Raise:

            CMError exception in-case of a failure.
        """
        cmclient.CMClient.__init__(self, server_ip, server_port, client_impl_module, verbose_logger)

    @cmclient.handle_exceptions
    def create_snapshot(self, snapshot_name):
        """initiate a create snapshot operation

           This API is used to initiate a create snapshot operation for the configuration
           data.

           Arguments:

           snapshot_name: The name of the snapshot

           Raise:

           CMError is raised in-case of a failure.
        """
        return self.client_lib.create_snapshot(snapshot_name)

    @cmclient.handle_exceptions
    def restore_snapshot(self, snapshot_name):
        """initiate a snapshot restore operation

           This API is used to initiate a snapshot restore operation for the
           configuration data.

           Arguments:

           snapshot_name: The name of the snapshot.

           Raise:

           CMError is raised in-case of a failure.
        """
        return self.client_lib.restore_snapshot(snapshot_name)

    @cmclient.handle_exceptions
    def delete_snapshot(self, snapshot_name):
        """initiate a snapshot delete operation

           This API is used to initiate a snapshot delete operation for the
           configuration data.

           Arguments:

           snapshot_name: The name of the snapshot.

           Raise:

           CMError is raised in-case of a failure.
        """
        return self.client_lib.delete_snapshot(snapshot_name)

    @cmclient.handle_exceptions
    def list_snapshots(self):
        """initiate a list snapshots operation

           This API is used to initiate a list snapshots operation for the
           configuration data.

           Arguments:

           Raise:

           CMError is raised in-case of a failure.
        """
        return self.client_lib.list_snapshots()

    @cmclient.handle_exceptions
    def activate(self, node_name):
        """activate configuration in all or one specific node

           This API is used to initiate full activation for all or one specific node

           Arguments:

           node_name: a string containing the node name where
                      the configuration is to be activated. If not specified, then activation
                      is done for all nodes.

           Raise:

           CMError is raised in-case of failure.
        """
        return self.client_lib.activate(node_name)

    @cmclient.handle_exceptions
    def activate_node(self, node_name):
        """for cmagent to activate configuration in specified node

           This API is used only by cmagent to initiate full activation for a node

           Arguments:

           node_name: a string containing the name of the node to be activated.

           Raise:

           CMError is raised in-case of failure.
        """
        return self.client_lib.activate_node(node_name)

    @cmclient.handle_exceptions
    def reboot_node(self, node_name):
        """request reboot of specified node

           This API is used to initiate node reboot during full activation of a node

           Arguments:

           node_name: a string containing the name of the node to be rebooted

           Raise:

           CMError is raised in-case of failure.
        """
        return self.client_lib.reboot_node(node_name)

    @cmclient.handle_exceptions
    def disable_automatic_activation(self):
        """disable automatic activation

           This API is used to disable automatic activation

           Arguments:

           Raise:

           CMError is raised in-case of failure.
        """
        return self.client_lib.disable_automatic_activation()

    @cmclient.handle_exceptions
    def enable_automatic_activation(self):
        """enable automatic activation

           This API is used to enable automatic activation

           Arguments:

           Raise:

           CMError is raised in-case of failure.
        """
        return self.client_lib.enable_automatic_activation()
