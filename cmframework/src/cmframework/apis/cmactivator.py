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
import os
import subprocess
import pwd
import logging

from cmframework.apis import cmerror


class CMActivator(object):
    ansible_bin = '/usr/local/bin/openstack-ansible'
    admin_user_file = '/etc/admin_user'

    def __init__(self):
        self.plugin_client = None
        try:
            with open(CMActivator.admin_user_file, 'r') as f:
                self.admin_user = f.read()
        except IOError:
            pass

    # pylint: disable=no-self-use
    def get_subscription_info(self):
        """get the subscription filter

           This API is used to get the re for matching the properties which the
           activation plugin is concerned about.

           Return:

           A string representing the regular expression used to match the
           properties which the activation plugin is concerned about.

           Raise:

           CMError can be raised in-case of a failure.
        """
        raise cmerror.CMError('Not implemented')

    # pylint: disable=no-self-use, unused-argument
    def activate_set(self, props):
        """activate a configuration data addition/update

           Arguments:

           props: A dictionary of name-value pairs representing the changed
           properties.

           Raise:

           CMError can be raised in-case of an error
        """
        raise cmerror.CMError('Not implemented')

    # pylint: disable=no-self-use, unused-argument
    def activate_delete(self, props):
        """activate a configuration data deletion

           Arguments:

           props: A list of deleted property names.

           Raise:

           CMError can be raised in-case of an error
        """
        raise cmerror.CMError('Not implemented')

    # pylint: disable=no-self-use, unused-argument
    def activate_full(self, target):
        """perform a full activation

           Arguments:

           target: None if activating all nodes
                   Node name string if activating only one node

           Raise:

           CMError can be raised in-case of an error
        """
        raise cmerror.CMError('Not implemented')

    # pylint: disable=no-self-use
    def get_plugin_client(self):
        """get the plugin client object

           This API can be used by the plugin to get the client object which the
           plugin can use to access the configuration data. Notice that the data
           accessed by this is what is stored in the backend. The changed data
           is passed as argument to the different validate functions.

           Return:

           The plugin client object
        """
        return self.plugin_client

    def run_playbook(self, playbook, target=None):
        playbook_dir = os.path.dirname(playbook)

        arguments = []
        arguments.append('-b')
        arguments.append('-u {}'.format(self.admin_user))
        if target:
            arguments.append('--limit {}'.format(target))
        arguments.append(playbook)

        cmd = '{} {}'.format(CMActivator.ansible_bin, ' '.join(arguments))
        out, result = self._run_cmd_as_user(cmd, playbook_dir, self.admin_user)
        if result != 0:
            raise cmerror.CMError('Playbook {} failed: {}'.format(playbook, out))
        logging.debug('Playbook out: %s', out)

    def _run_cmd_as_user(self, cmd, cwd, user):
        pw_record = pwd.getpwnam(user)
        user_name = pw_record.pw_name
        user_home_dir = pw_record.pw_dir
        user_uid = pw_record.pw_uid
        user_gid = pw_record.pw_gid
        env = os.environ.copy()
        env['CONFIG_PHASE'] = 'postconfig'
        env['HOME'] = user_home_dir
        env['LOGNAME'] = user_name
        env['PWD'] = cwd
        env['USER'] = user_name
        p = subprocess.Popen(cmd.split(), preexec_fn=self._demote(user_uid, user_gid),
                             cwd=cwd, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        out, _ = p.communicate()
        return (out, p.returncode)

    def _demote(self, user_uid, user_gid):
        def result():
            os.setgid(user_gid)
            os.setuid(user_uid)

        return result


class CMGlobalActivator(CMActivator):
    def __init__(self):
        super(CMGlobalActivator, self).__init__()


class CMLocalActivator(CMActivator):
    def __init__(self):
        super(CMLocalActivator, self).__init__()
        self.hostname = None

    def get_hostname(self):
        """get the node name

           This API is used to get the name of the node where activation is
           ongoing.

           Return:

           The node name
        """
        return self.hostname


def main():
    def print_type(activator):
        if isinstance(activator, CMLocalActivator):
            print 'Local activator'
        elif isinstance(activator, CMActivator):
            print 'Activator'
        else:
            print 'Unknown'

    activator = CMActivator()
    localactivator = CMLocalActivator()

    x = 100

    print_type(activator)
    print_type(localactivator)
    print_type(x)


if __name__ == '__main__':
    main()
