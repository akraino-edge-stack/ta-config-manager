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
from cmdatahandlers.api import utils


class Config(config.Config):
    def __init__(self, confman):
        super(Config, self).__init__(confman)
        self.ROOT = 'cloud.storage_profiles'
        self.DOMAIN = 'storage_profiles'

    def init(self):
        pass

    def validate(self):
        self.validate_root()
        self._validate_storage_profiles()

    def _validate_storage_profiles(self):
        profiles = self.get_storage_profiles()
        utils.validate_list_items_unique(profiles)
        for profile in profiles:
            self._validate_storage_profile(profile)

    def _validate_storage_profile(self, profile):
        backend = self.get_profile_backend(profile)
        storageconf = self.confman.get_storage_config_handler()
        backends = storageconf.get_storage_backends()
        if backend not in backends:
            raise configerror.ConfigError(
                'Invalid backend %s provided in profile %s' % (backend, profile))
        if backend == 'ceph':
            self.get_profile_nr_of_ceph_osd_disks(profile)
        elif backend == 'lvm':
            self.get_profile_lvm_cinder_storage_partitions(profile)
            self.get_profile_lvm_instance_storage_partitions(profile)
            self.get_profile_lvm_instance_cow_lv_storage_percentage(profile)
            self.get_profile_instance_storage_percentage(profile)

    def is_valid_profile(self, profile):
        self.validate_root()
        profiles = self.get_storage_profiles()
        if profile not in profiles:
            raise configerror.ConfigError('Invalid profile name %s' % profile)

    def get_storage_profiles(self):
        """ get the storage profiles list

            Return:

            A list of storage profile(s) names

            Raise:

            ConfigError in-case of an error
        """
        return self.config[self.ROOT].keys()

    def get_profile_ceph_osd_disks(self, profile):
        """ get the ceph osd disks

            Argument:

            profile name

            Return:

            The ceph osd disks

            Raise:

            ConfigError in-case of an error
        """
        return self._get_attribute(profile, 'ceph_osd_disks')

    def get_profile_ceph_osd_journal_disk(self, profile):
        """ get the ceph osd journal disk

            Argument:

            profile name

            Return:

            The ceph osd journal disk

            Raise:

            ConfigError in-case of an error
        """
        return self._get_attribute(profile, 'ceph_osd_journal_disk')

    def get_profile_ceph_openstack_pg_proportion(self, profile):
        openstack_pg_ratio, caas_pg_ratio = self._get_ceph_pg_share_ratios(profile)
        return openstack_pg_ratio / (openstack_pg_ratio + caas_pg_ratio)

    def _get_ceph_pg_share_ratios(self, profile):
        pg_share_ratios = self.get_profile_ceph_openstack_caas_pg_ratio(profile).split(':')
        return map(lambda r: float(r), pg_share_ratios)

    def get_profile_ceph_caas_pg_proportion(self, profile):
        openstack_pg_ratio, caas_pg_ratio = self._get_ceph_pg_share_ratios(profile)
        return caas_pg_ratio / (openstack_pg_ratio + caas_pg_ratio)

    def get_profile_ceph_openstack_caas_pg_ratio(self, profile):
        """ get the ceph openstack-caas pg share ratio

            Argument:

            profile name

            Return:

            The ceph osd share ratio

            Raise:

            ConfigError in-case of an error
        """
        return self._get_optional_attribute(
            profile, 'ceph_pg_openstack_caas_share_ratio', "1:0")

    def get_profile_nr_of_ceph_osd_disks(self, profile):
        """ get the number of ceph osd disks

            Argument:

            profile name

            Return:

            The number of ceph osd disks

            Raise:

            ConfigError in-case of an error
        """
        self.validate_root()
        self.is_valid_profile(profile)

        if 'nr_of_ceph_osd_disks' not in self.config[self.ROOT][profile]:
            ceph_osd_disks = self._get_attribute(profile, 'ceph_osd_disks')
            return len(ceph_osd_disks)
        return self.config[self.ROOT][profile]['nr_of_ceph_osd_disks']

    def get_profile_lvm_cinder_storage_partitions(self, profile):
        """ get the lvm_cinder_storage_partitions

            Argument:

            profile name

            Return:

            The lvm_cinder_storage_partitions

            Raise:

            ConfigError in-case of an error
        """
        return self._get_attribute(profile, 'lvm_cinder_storage_partitions')

    def get_profile_backend(self, profile):
        """ get the storage profile backend

            Argument:

            profile name

            Return:

            The profile backend

            Raise:

            ConfigError in-case of an error
        """
        return self._get_attribute(profile, 'backend')

    def get_profile_lvm_instance_storage_partitions(self, profile):
        """ get the lvm_instance_storage_partitions

            Argument:

            profile name

            Return:

            The lvm_instance_storage_partitions

            Raise:

            ConfigError in-case of an error
        """
        return self._get_attribute(profile, 'lvm_instance_storage_partitions')

    def get_profile_lvm_instance_cow_lv_storage_percentage(self, profile):
        """ get the lvm_instance_cow_lv_storage_percentage

            Argument:

            profile name

            Return:

            The lvm_instance_cow_lv_storage_percentage

            Raise:

            ConfigError in-case of an error
        """
        return self._get_attribute(profile, 'lvm_instance_cow_lv_storage_percentage')

    def get_profile_instance_storage_percentage(self, profile):
        """ get the instance_storage_percentage

            Argument:

            profile name

            Return:

            The instance_storage_percentage

            Raise:

            ConfigError in-case of an error
        """
        return self._get_attribute(profile, 'instance_storage_percentage')

    def get_profile_bare_lvm_mount_options(self, profile):
        """ get the mount_options

            Argument:

            profile name

            Return:

            The mount_options

            Raise:

            ConfigError in-case of an error
        """
        return self._get_optional_attribute(profile, 'mount_options')

    def get_profile_bare_lvm_mount_dir(self, profile):
        """ get the mount_dir

            Argument:

            profile name

            Return:

            The mount_dir

            Raise:

            ConfigError in-case of an error
        """
        return self._get_attribute(profile, 'mount_dir')

    def get_profile_bare_lvm_lv_name(self, profile):
        """ get the lv_name

            Argument:

            profile name

            Return:

            The lv_name

            Raise:

            ConfigError in-case of an error
        """
        return self._get_attribute(profile, 'lv_name')

    def _get_attribute(self, profile, attribute):
        """ get arbirary storage profile attribute

            Arguments:

            - profile name
            - attribute name

            Return:

            The attribute

            Raise:

            ConfigError in-case of an error
        """
        self.validate_root()
        self.is_valid_profile(profile)
        if attribute not in self.config[self.ROOT][profile]:
            raise configerror.ConfigError(
                'Profile %s does not have %s configured' % (attribute, profile))
        return self.config[self.ROOT][profile][attribute]

    def _get_optional_attribute(self, profile, attribute, default_value=""):
        """ get arbirary optional storage profile attribute

            Arguments:

            - profile name
            - attribute name

            Return:

            The attribute

            Raise:

            ConfigError in-case of an error
        """
        self.validate_root()
        self.is_valid_profile(profile)
        if attribute not in self.config[self.ROOT][profile]:
            return default_value
        return self.config[self.ROOT][profile][attribute]
