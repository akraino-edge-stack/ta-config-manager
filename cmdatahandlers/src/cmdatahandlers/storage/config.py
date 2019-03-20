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

from cmdatahandlers.api import configerror
from cmdatahandlers.api import config


class Config(config.Config):
    def __init__(self, confman):
        super(Config, self).__init__(confman)
        self.ROOT = 'cloud.storage'
        self.DOMAIN = 'storage'

    def init(self):
        pass

    def validate(self):
        self.validate_root()
        self._validate_storage_backends()

    def _validate_storage_backends(self):
        backends = self.get_storage_backends()
        for backend in backends:
            if backend == 'ceph':
                self._validate_ceph_backend()
            elif backend == 'external_ceph':
                self._validate_external_ceph_backend()
            elif backend == 'lvm':
                self._validate_lvm_backend()
            else:
                raise configerror.ConfigError('Invalid backend %s specified' % backend)

    def _validate_ceph_backend(self):
        self.is_ceph_enabled()
        osdpoolsize = self.get_ceph_osd_pool_size()
        if osdpoolsize <= 1:
            raise configerror.ConfigError('Invalid osd pool size configured %d' % osdpoolsize)

    def _validate_external_ceph_backend(self):
        self.is_external_ceph_enabled()
        self.get_ext_ceph_fsid()
        self.get_ext_ceph_mon_hosts()
        self.get_ext_ceph_ceph_s3_endpoint()
        self.get_ext_ceph_ceph_s3_keystone_user()
        self.get_ext_ceph_ceph_s3_keystone_adminpw()
        self.get_ext_ceph_ceph_user()
        self.get_ext_ceph_ceph_user_key()
        self.get_ext_ceph_cinder_pool()
        self.get_ext_ceph_glance_pool()
        self.get_ext_ceph_nova_pool()
        self.get_ext_ceph_platform_pool()
        self.get_ext_ceph_cidr()

    def _validate_lvm_backend(self):
        self.is_lvm_enabled()

    def _set_hostlist(self, key, value):
        self.validate_root()
        if len(value) <= 0:
            raise configerror.ConfigError('The host list for {} is empty'.format(key))
        self.config[self.ROOT][key] = value

    def get_storage_backends(self):
        """ get the list of backends

            Return:

            A list of backend names

            Raise:

            ConfigError in-case of an error
        """
        self.validate_root()

        if 'backends' not in self.config[self.ROOT]:
            raise configerror.ConfigError('No backends configured')

        return self.config[self.ROOT]['backends'].keys()

    def get_ceph_osd_pool_size(self):
        """ get the ceph osd pool size

            Return:

            The ceph osd pool size

            Raise:

            ConfigError in-case of an error
        """
        self.validate_root()
        backends = self.get_storage_backends()

        if 'ceph' not in backends:
            raise configerror.ConfigError('No ceph backend configured')

        if 'osd_pool_default_size' not in self.config[self.ROOT]['backends']['ceph']:
            raise configerror.ConfigError('No ceph osd configuration found')

        return self.config[self.ROOT]['backends']['ceph']['osd_pool_default_size']

    def is_lvm_enabled(self):
        """ Is lvm enabled or not.

            Return:
                True if lvm is enabled otherwise False.
        """
        return self.is_backend_enabled('lvm')

    def is_ceph_enabled(self):
        """ Is ceph enabled or not.

            Return:
                True if ceph is enabled otherwise False.
        """
        return self.is_backend_enabled('ceph')

    def is_external_ceph_enabled(self):
        """ Is external ceph enabled or not.

            Return:
                True if external ceph is enabled otherwise False.
        """
        return self.is_backend_enabled('external_ceph')

    def is_backend_enabled(self, backend):
        """ Is the given backend enabled.

            Argument:
                The storage backend.

            Return:
                True if the backend is enabled otherwise False.

            Raise:
                -
        """
        self.validate_root()
        backends = self.get_storage_backends()

        if backend not in backends:
            return False

        if 'enabled' not in self.config[self.ROOT]['backends'][backend]:
            raise configerror.ConfigError(
                'The enabled parameter not configured for {}'.format(backend))

        return self.config[self.ROOT]['backends'][backend]['enabled']

    def get_enabled_backends(self):
        """ Gets enabled storage backends.

            Argument:
                The storage backend.

            Return:
                List of enabled backends.
        """
        return [backend for backend, values in self.config[self.ROOT]['backends'].iteritems()
                if values.get('enabled', False)]

    def set_mons(self, hosts):
        """ Set the ceph monitors

            Argument:

            A list of ceph monitor hosts.

            Raise:

            ConfigError in-case of an error
        """
        self._set_hostlist('mons', hosts)

    def set_ceph_mons(self, hosts):
        """ Set the ceph monitors for openstack-ansible.

            Argument:

            A list of ceph monitor hosts.

            Raise:

            ConfigError in-case of an error
        """
        self._set_hostlist('ceph_mons', hosts)

    def set_osds(self, hosts):
        """ Set the ceph osds

            Argument:

            A list of ceph osd hosts.

            Raise:

            ConfigError in-case of an error
        """
        self._set_hostlist('osds', hosts)

    def _get_external_ceph_attribute(self, attribute):
        return self._get_backends_attribute('external_ceph', attribute)

    def _is_valid_backend(self, backend):
        self.validate_root()
        if backend not in self.config[self.ROOT]['backends']:
            raise configerror.ConfigError(
                'The cloud.storage.backends does not have the '
                'backend {} configured'.format(backend))

    def _is_valid_backends_attribute(self, backend, attribute):
        self.validate_root()
        if attribute not in self.config[self.ROOT]['backends'][backend]:
            raise configerror.ConfigError(
                'The cloud.storage.backends.{} does not have '
                'the attribute {} configured'.format(backend, attribute))

    def _get_backends_attribute(self, backend, attribute):
        self.validate_root()
        self._is_valid_backend(backend)
        self._is_valid_backends_attribute(backend, attribute)
        return self.config[self.ROOT]['backends'][backend][attribute]

    def get_ext_ceph_fsid(self):
        """ Get the file system id of the external ceph cluster.

            Return:
                The fsid of the external ceph cluster.

            Raise:
                ConfigError in-case of an error
        """
        return self._get_external_ceph_attribute('fsid')

    def get_ext_ceph_mon_hosts(self):
        """ Get the monitor hosts of the external ceph system.

            Return:
                A list of monitor hosts.

            Raise:
                ConfigError in-case of an error
        """
        return self._get_external_ceph_attribute('mon_hosts')

    def get_ext_ceph_ceph_s3_endpoint(self):
        """ Get the ceph s3 endpoint. The endpoint consists of a
            service name and port.

            Return:
                A ceph s3 endpoint in format: <service>:<port>

            Raise:
                ConfigError in-case of an error
        """
        return self._get_external_ceph_attribute('ceph_s3_endpoint')

    def get_ext_ceph_ceph_s3_keystone_user(self):
        """ Get the ceph s3 endpoint user.

            Return:
                The external ceph s3 keystone user.

            Raise:
                ConfigError in-case of an error.
        """
        return self._get_external_ceph_attribute('ceph_s3_keystone_user')

    def get_ext_ceph_ceph_s3_keystone_adminpw(self):
        """ Get the ceph s3 endpoint adminpw.

            Return:
                The external ceph s3 keystone adminpw.

            Raise:
                ConfigError in-case of an error.
        """
        return self._get_external_ceph_attribute('ceph_s3_keystone_adminpw')

    def get_ext_ceph_ceph_user(self):
        """ Get the ceph user of the external ceph server.

            Return:
                The external ceph user.

            Raise:
                ConfigError in-case of an error
        """
        return self._get_external_ceph_attribute('ceph_user')

    def get_ext_ceph_ceph_user_key(self):
        """ Get the external ceph server ceph user key.

            Return:
                The external ceph user key.

            Raise:
                ConfigError in-case of an error
        """
        return self._get_external_ceph_attribute('ceph_user_key')

    def get_ext_ceph_cinder_pool(self):
        """ Get the external ceph server cinder pool name.

            Return:
                External ceph server cinder pool name.

            Raise:
                ConfigError in-case of an error
        """
        return self._get_external_ceph_attribute('cinder_pool')

    def get_ext_ceph_glance_pool(self):
        """ Get the external ceph server glance pool name.

            Return:
                External ceph server glance pool name.

            Raise:
                ConfigError in-case of an error
        """
        return self._get_external_ceph_attribute('glance_pool')

    def get_ext_ceph_nova_pool(self):
        """ Get the external ceph server nova pool name.

            Return:
                External ceph server nova pool name.

            Raise:
                ConfigError in-case of an error
        """
        return self._get_external_ceph_attribute('nova_pool')

    def get_ext_ceph_platform_pool(self):
        """ Get the external ceph server platform pool name.

            Return:
                External ceph server platform pool name.

            Raise:
                ConfigError in-case of an error
        """
        return self._get_external_ceph_attribute('platform_pool')

    def get_ext_ceph_cidr(self):
        """ Get the external ceph cidr.

            Return:
                External ceph cidr.

            Raise:
                ConfigError in-case of an error
        """
        return self._get_external_ceph_attribute('cidr')

    def set_ceph_enabled(self):
        """ Set the ceph enabled

            Raise:

            ConfigError in-case of an error
        """

        if 'backends' not in self.config[self.ROOT]:
            raise configerror.ConfigError('No backends configured')

        if 'external_ceph' in self.config[self.ROOT]['backends']:
            return

        if self.is_lvm_enabled():
            return

        try:
            self.is_ceph_enabled()
        except configerror.ConfigError:
            self.config[self.ROOT]['backends']['ceph'].update({"enabled": True})

    def mask_sensitive_data(self):
        if 'external_ceph' in self.get_storage_backends():
            self.config[self.ROOT]['backends']['external_ceph']['ceph_user_key'] = self.MASK
            self.config[self.ROOT]['backends']['external_ceph']['ceph_s3_keystone_adminpw'] = self.MASK
