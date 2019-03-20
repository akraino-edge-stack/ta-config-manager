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

from functools import wraps
from cmframework import apis as cmapis


def handle_exceptions(func):
    @wraps(func)
    def wrapper(self, *arg, **kwargs):
        try:
            return func(self, *arg, **kwargs)
        except cmapis.cmerror.CMError as exp:
            raise
        except Exception as exp:
            raise cmapis.cmerror.CMError(str(exp))

    return wrapper


class CMClient(object):
    """
        Usage Example:
            class VerboseLogger:
                def __call__(self, msg):
                    print(msg)

            logger = VerboseLogger()

            client = CMClient(192.128.254.10, 51110, cmclient.CMClientImpl, logger)
            try:
                value = client.get_property('controller-1.ntp.servers')
            except cmapis.cmerror.CMError as error:
                print('Got exception %s' % str(error))
    """

    @handle_exceptions
    def __init__(self, server_ip='config-manager', server_port=61100,
                 client_lib_impl_module='cmframework.lib.CMClientImpl', verbose_logger=None):
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

        import socket
        try:
            serverip = socket.gethostbyname(server_ip)
        except Exception:  # pylint: disable=broad-except
            # use localhost in-case we cannot resolve the provided hostname
            serverip = '127.0.0.1'

        self.server_ip = serverip
        self.server_port = server_port
        self.client_lib = None
        self.verbose_logger = verbose_logger

        # Separate class path and module name
        parts = client_lib_impl_module.rsplit('.', 1)
        module_path = parts[0]
        class_name = parts[1]
        self.verbose_log('module_path = %s' % module_path)
        self.verbose_log('class_name = %s' % class_name)
        module = __import__(module_path, fromlist=[module_path])
        classobj = getattr(module, class_name)
        self.client_lib = classobj(self.server_ip, self.server_port, verbose_logger)

    def verbose_log(self, msg):
        if self.verbose_logger:
            self.verbose_logger(msg)

    @handle_exceptions
    def get_property(self, prop_name, snapshot_name=None):
        """get the value assoicated with a property.

           This is the API used to read the value associated with a
           configuration property.

           Arguments:

           prop_name: The property name
           (optional) snapshot_name: The snapshot name

           Raise:

           CMError in-case of a failure.
        """
        result = self.client_lib.get_property(prop_name, snapshot_name)
        return result

    @handle_exceptions
    def get_properties(self, prop_filter, snapshot_name=None):
        """get a set of properties matching a filter.

           This is the API used to read a group of properties matching some
           filter.

           Arguments:

           prop_filter: A valid python re describing the filter used when
                        matching the returned properties.
           (optional) snapshot_name: The snapshot name

          Raise:

          CMError is raised in-case of a failure.
        """
        self._check_filter(prop_filter)
        result = self.client_lib.get_properties(prop_filter, snapshot_name)
        return result

    @handle_exceptions
    def set_property(self, prop_name, prop_value):
        """set/update the value of a property.

            This is the API used to set/update the value associated with a
            property.

            Arguments:

            prop_name: A string representing the property name.

            prop_value: A string representing the property value.

            Raise:

            CMError is raised in-case of failure.
        """
        return self.client_lib.set_property(prop_name, prop_value)

    @handle_exceptions
    def set_properties(self, props, overwrite=False):
        """set/update a group of properties as a whole

           This API is used to set/update the values associated with a group of
           properties as a whole, the change is either accepted as a whole or
           rejected as a whole.

           Arguments:

           props: A dictionary containing the changed properties.

           overwrite: Replace the existing configuration dictionary with the new one.

           Raise:

           CMError is raised in-case of a failure.
        """
        return self.client_lib.set_properties(props, overwrite)

    @handle_exceptions
    def delete_property(self, prop_name):
        """delete a property

           This is the API used to delete a configuration property.

           Arguments:

           prop_name: The name of the property to be deleted.

           Raise:

           CMError is raised in-case of a failure.
        """
        return self.client_lib.delete_property(prop_name)

    @handle_exceptions
    def delete_properties(self, arg):
        """delete a group of properties as a whole

           This is the API used to delete a group of properties as whole, if the
           deletion of one of the properties is rejected then the whole delete
           operation will fail.

           Arguments:

           arg: This can be either a string representing the re used when
                matching the properties to be deleted, or it can be a list of
                properties names to be deleted.

            Raise:

            CMError is raised in-case of a failure.
        """
        if isinstance(arg, str):
            self._check_filter(arg)
        return self.client_lib.delete_properties(arg)

    @handle_exceptions
    def get_changes_states(self, change_uuid):
        """get the config changes states

           This is the API used to get the changes states

           Arguments:

           arg: This can be either a valid change uuid or None.

           Raise:

            CMError is raised in-case of a failure.
        """
        return self.client_lib.get_changes_states(change_uuid)

    @handle_exceptions
    def wait_activation(self, change_uuid):
        """wait for activation of config changes to finish

           This is the API used to wait for config changes to finish

           Arguments:

           arg: A valid change uuid.

           Raise:

            CMError is raised in-case of a failure.
        """
        return self.client_lib.wait_activation(change_uuid)

    # pylint: disable=no-self-use
    def _check_filter(self, prop_filter):
        re.compile(prop_filter)
