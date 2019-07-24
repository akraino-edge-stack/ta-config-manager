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

from cmdatahandlers.api import config
from cmdatahandlers.api import utils
from cmdatahandlers.api import configerror
from serviceprofiles import profiles
import yaml
import jinja2
import string
from random import choice

CAAS_CONFIG_FILE_PATH = "/etc/cmframework/config/"
CAAS_CONFIG_FILE = "caas.yaml"
DEFAULT_CAAS_DNS_DOMAIN = "rec.io"
VNF_EMBEDDED_SOFT_EVICTION_THRESHOLD = "300Mi"
BM_SOFT_EVICTION_THRESHOLD = "4Gi"
VNF_EMBEDDED_HARD_EVICTION_THRESHOLD = "200Mi"
BM_HARD_EVICTION_THRESHOLD = "2Gi"
ADMIN_PWD_LENGTH = 20
DEFAULT_CAAS_INFRA_LOG_TYPE = 'remote_syslog'


class Config(config.Config):
    valid_redundancy_models = ['non-redundant', 'active-cold-standby']

    def __init__(self, confman):
        super(Config, self).__init__(confman)
        self.ROOT = 'cloud.caas'
        self.DOMAIN = 'caas'

    def init(self):
        pass

    @staticmethod
    def validate():
        print("validate")

    def flavour_set(self):
        hostsconf = self.confman.get_hosts_config_handler()
        caas_masters = []
        for host in hostsconf.get_hosts():
            if 'caas_master' in hostsconf.get_service_profiles(host):
                caas_masters.append(host)
        return "multi" if len(caas_masters) > 1 else "single"

    def set_dynamic_config(self):
        if utils.is_virtualized():
            self.config[self.ROOT]['vnf_embedded_deployment'] = self.get_vnf_flag()
        user_conf = self.confman.get_users_config_handler()
        self.set_caas_parameter('helm_home', "/home/{}/.helm".format(user_conf.get_admin_user()))
        self.set_caas_parameter('flavour', self.flavour_set())
        admin_pwd = self.get_caas_parameter('admin_password')
        self.config[self.ROOT]['admin_password'] = \
                admin_pwd if admin_pwd != '' else self.generate_pwd(ADMIN_PWD_LENGTH)
        if not self.get_caas_parameter('dns_domain'):
            self.set_caas_parameter('dns_domain', DEFAULT_CAAS_DNS_DOMAIN)
        if not self.get_caas_parameter('infra_log_store'):
            self.set_caas_parameter('infra_log_store', DEFAULT_CAAS_INFRA_LOG_TYPE)
        if not self.get_caas_parameter('log_forwarding'):
            self.set_caas_parameter('log_forwarding', [])
        hostsconf = self.confman.get_hosts_config_handler()
        hostsconf.set_nodeindex()

    def set_static_config(self):
        try:
            template = jinja2.Environment(
                loader=jinja2.FileSystemLoader(
                    CAAS_CONFIG_FILE_PATH)).get_template(CAAS_CONFIG_FILE)
            with open(CAAS_CONFIG_FILE_PATH + CAAS_CONFIG_FILE) as config_file:
                data = yaml.load(config_file)
            self.config[self.ROOT].update(
                self._template_config(template, self.config[self.ROOT], data))
        except jinja2.exceptions.TemplateNotFound:
            return
        except Exception:
            raise configerror.ConfigError("Unexpected issue has occured!")

    def set_post_config(self):
        self.config[self.ROOT]['swift_credential'] = \
            dict(
                user=self.get_caas_parameter('swift_credential').get('user'),
                tenant=self.get_caas_parameter('swift_credential').get('tenant'),
                password=self.generate_pwd(ADMIN_PWD_LENGTH)
            )

    @staticmethod
    def _template_config(template, base_config, initial_data):
        config_data = initial_data.copy()
        config_data.update(base_config)
        output_text = template.render(config_data)
        previous_output_text = ""
        while output_text != previous_output_text:
            config_data = yaml.load(output_text)
            config_data.update(base_config)
            output_text = template.render(config_data)
            previous_output_text = output_text
        return yaml.load(output_text)

    def add_defaults(self):
        if not self.config.get('cloud.caas', ''):
            return
        self.set_dynamic_config()
        self.set_static_config()
        self.set_post_config()

    def is_vnf_embedded_deployment(self):
        return self.get_caas_only() and self.get_vnf_flag()

    def get_vnf_flag(self):
        return bool(self.config.get(self.ROOT, {}).get('vnf_embedded_deployment',
                                                  False))

    def get_caas_only(self):
        return self.is_caas_deployment() and not self.is_openstack_deployment()

    def is_openstack_deployment(self):
        return bool(self.get_controller_hosts())

    def is_caas_deployment(self):
        return bool(self.get_caas_master_hosts())

    def is_hybrid_deployment(self):
        return self.is_caas_deployment() and self.is_openstack_deployment()

    def get_caas_master_hosts(self):
        service_profiles_lib = profiles.Profiles()
        return self._get_hosts_for_service_profile(service_profiles_lib.get_caasmaster_service_profile())

    def _get_hosts_for_service_profile(self, profile):
        hostsconf = self.confman.get_hosts_config_handler()
        return hostsconf.get_service_profile_hosts(profile)

    def get_controller_hosts(self):
        service_profiles_lib = profiles.Profiles()
        return self._get_hosts_for_service_profile(service_profiles_lib.get_controller_service_profile())

    def get_apiserver_in_hosts(self):
        return self.config.get(self.ROOT, {}).get('apiserver_in_hosts', '')

    def get_registry_url(self):
        return self.config.get(self.ROOT, {}).get('registry_url', '')

    def get_update_registry_url(self):
        return self.config.get(self.ROOT, {}).get('update_registry_url', '')

    def get_swift_url(self):
        return self.config.get(self.ROOT, {}).get('swift_url', '')

    def get_swift_update_url(self):
        return self.config.get(self.ROOT, {}).get('swift_update_url', '')

    def get_ldap_master_url(self):
        return self.config.get(self.ROOT, {}).get('ldap_master_url', '')

    def get_ldap_slave_url(self):
        return self.config.get(self.ROOT, {}).get('ldap_slave_url', '')

    def get_chart_repo_url(self):
        return self.config.get(self.ROOT, {}).get('chart_repo_url', '')

    def get_tiller_url(self):
        return self.config.get(self.ROOT, {}).get('tiller_url', '')

    def get_apiserver_svc_ip(self):
        return self.config.get(self.ROOT, {}).get('apiserver_svc_ip', '')

    def get_caas_parameter(self, parameter):
        return self.config.get(self.ROOT, {}).get(parameter, '')

    def set_caas_parameter(self, parameter, value):
        self.config[self.ROOT][parameter] = value

    def get_admin_password(self):
        return self.config.get(self.ROOT, {}).get('admin_password')

    @staticmethod
    def generate_pwd(pwd_length):
        character_pool = string.ascii_letters + string.digits
        return ''.join(choice(character_pool) for i in range(pwd_length))

    def get_kubernetes_domain(self):
        return 'kubernetes.default.svc.{}'.format(
            self.config.get(self.ROOT, {}).get('dns_domain', ''))

    def get_caas_soft_eviction_threshold(self):
        if self.is_vnf_embedded_deployment():
            return VNF_EMBEDDED_SOFT_EVICTION_THRESHOLD
        else:
            return BM_SOFT_EVICTION_THRESHOLD

    def get_caas_hard_eviction_threshold(self):
        if self.is_vnf_embedded_deployment():
            return VNF_EMBEDDED_HARD_EVICTION_THRESHOLD
        else:
            return BM_HARD_EVICTION_THRESHOLD
