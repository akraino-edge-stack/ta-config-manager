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

from unittest import TestCase
from cmdatahandlers.api import configmanager
import cmdatahandlers.performance_profiles.config
from cmdatahandlers.api.configerror import ConfigError


class PerformanceProfilesConfigTest(TestCase):


    profile = 'dpdk_profile'
    profile_data = {profile: {'platform_cpus': {'numa0': 1, 'numa1': 1},
                              'ovs_dpdk_cpus': {'numa0': 2, 'numa1': 2},
                              'default_hugepagesz': '1M',
                              'hugepagesz': '1G',
                              'hugepages': 192
                             }
                   }
    hosts_data = {'controller-1':{'service_profiles': ['controller']}}

    config = {'cloud.performance_profiles': profile_data,
              'cloud.hosts': hosts_data }

    fail_profile ='dpdk_fail_profile'
    config_fail = {'cloud.performance_profiles': {fail_profile: {} },
                   'cloud.hosts': hosts_data }

    def setUp(self):
        confman = configmanager.ConfigManager(self.config)
        self.pp_handler = confman.get_performance_profiles_config_handler()

        confman_fail = configmanager.ConfigManager(self.config_fail)
        self.pp_handler_fail = confman_fail.get_performance_profiles_config_handler()

    def test_validate(self):
        self.pp_handler.validate()

    def test_is_valid_profile_raises_error(self):
        with self.assertRaisesRegexp(ConfigError, "Invalid profile name foo_profile"):
            self.pp_handler.is_valid_profile('foo_profile')

    def test_get_performance_profiles(self):
        profiles_data = self.pp_handler.get_performance_profiles()
        expected_data = [self.profile]
        self.assertEqual(profiles_data, expected_data)

    def test_get_profile_default_hugepage_size(self):
        default_hugepagesz_data = self.pp_handler.get_profile_default_hugepage_size(self.profile)
        expected_data = '1M'
        self.assertEqual(default_hugepagesz_data, expected_data)

    def test_get_profile_default_hugepage_size_raises_error(self):
        error_text = "Profile {} does not have default_hugepagesz".format(self.fail_profile)
        with self.assertRaisesRegexp(ConfigError, error_text):
            self.pp_handler_fail.get_profile_default_hugepage_size(self.fail_profile)

    def test_get_profile_hugepage_size(self):
        hugepagesz_data = self.pp_handler.get_profile_hugepage_size(self.profile)
        expected_data = '1G'
        self.assertEqual(hugepagesz_data, expected_data)

    def test_get_profile_hugepage_size_raises_error(self):
        error_text = "Profile {} does not have hugepagesz".format(self.fail_profile)
        with self.assertRaisesRegexp(ConfigError, error_text):
            self.pp_handler_fail.get_profile_hugepage_size(self.fail_profile)

    def test_get_profile_hugepage_count(self):
        hugepages_data = self.pp_handler.get_profile_hugepage_count(self.profile)
        expected_data = 192
        self.assertEqual(hugepages_data, expected_data)

    def test_get_profile_hugepage_count_raises_error(self):
        error_text = "Profile {} does not have hugepages".format(self.fail_profile)
        with self.assertRaisesRegexp(ConfigError, error_text):
            self.pp_handler_fail.get_profile_hugepage_count(self.fail_profile)

    def test_get_platform_cpus(self):
        platform_cpus_data = self.pp_handler.get_platform_cpus(self.profile)
        expected_data = {'numa0': 1, 'numa1': 1}
        self.assertEqual(platform_cpus_data, expected_data)

    def test_get_platform_cpus_raises(self):
        error_text = "Profile {} does not have platform_cpus".format(self.fail_profile)
        with self.assertRaisesRegexp(ConfigError, error_text):
            self.pp_handler_fail.get_platform_cpus(self.fail_profile)

    def test_get_ovs_dpdk_cpus(self):
        ovs_dpdk_cpus_data = self.pp_handler.get_ovs_dpdk_cpus(self.profile)
        expected_data = {'numa0': 2, 'numa1': 2}
        self.assertEqual(ovs_dpdk_cpus_data, expected_data)

    def test_get_ovs_dpdk_cpus_raises_error(self):
        error_text = "Profile {} does not have ovs_dpdk_cpus".format(self.fail_profile)
        with self.assertRaisesRegexp(ConfigError, error_text):
            self.pp_handler_fail.get_ovs_dpdk_cpus(self.fail_profile)

    def test__fill_option_value(self):
        data = {}
        self.pp_handler._fill_option_value(data, self.profile, 'platform_cpus', None)
        self.assertEqual(data, {'platform_cpus': {'numa0': 1, 'numa1': 1}})
        self.pp_handler._fill_option_value(data, self.profile, 'platform_cpus', {'numa0': 5})
        self.assertEqual(data, {'platform_cpus': {'numa0': 5}})

    def test_update(self):
        cman = configmanager.ConfigManager({'cloud.performance_profiles': {}, 'cloud.hosts': self.hosts_data})
        h = cman.get_performance_profiles_config_handler()
        profile = 'niksnaks'
        platform_cpus = {'numa0': 1, 'numa1': 1}
        ovs_dpdk_cpus = {'numa0': 2, 'numa1': 2}
        hugepages = 8
        h.update(profile, platform_cpus, ovs_dpdk_cpus, hugepages)
        self.assertEqual(h.get_performance_profiles(), [profile])
        self.assertEqual(h.get_platform_cpus(profile), platform_cpus)
        self.assertEqual(h.get_ovs_dpdk_cpus(profile), ovs_dpdk_cpus)
        self.assertEqual(h.get_profile_hugepage_count(profile), hugepages)
        with self.assertRaisesRegexp(ConfigError, 'Profile niksnaks does not have hugepagesz'):
            h.get_profile_hugepage_size(profile)
        with self.assertRaisesRegexp(ConfigError, 'Profile niksnaks does not have default_hugepagesz'):
            h.get_profile_default_hugepage_size(profile)

    def test_delete(self):
        cman = configmanager.ConfigManager({'cloud.performance_profiles': {}, 'cloud.hosts': self.hosts_data})
        h = cman.get_performance_profiles_config_handler()
        profile = 'nice_profile'
        h.update(profile, '1-8', '4', 2)
        h.delete(profile)
        error_text = 'Invalid profile name {}'.format(profile)
        self.assertEqual(h.get_performance_profiles(), [])
        with self.assertRaisesRegexp(ConfigError, error_text):
            h.delete(profile)

    def test_dump(self):
        data = self.pp_handler.dump()
        self.assertEqual(data, self.profile_data)


if __name__ == '__main__':
    unittest.main()
