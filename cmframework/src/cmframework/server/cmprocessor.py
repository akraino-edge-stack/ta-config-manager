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

from cmframework.utils import cmactivationwork
from cmframework.server import cmeventletrwlock
from cmframework.server import cmcsn
from cmframework.server import cmsnapshot
from cmframework.utils.cmflagfile import CMFlagFile
from cmframework.utils import cmalarm


class CMProcessor(object):
    SERVICE_GROUP_NAME = 'config-manager'

    def __init__(self,
                 backend_handler,
                 validator,
                 activator,
                 changemonitor,
                 activationstate_handler,
                 snapshot_handler):
        logging.debug('CMProcessor constructed')

        self.backend_handler = backend_handler
        self.lock = cmeventletrwlock.CMEventletRWLock()
        self.csn = cmcsn.CMCSN(self.backend_handler)
        self.validator = validator
        self.activator = activator
        self.reboot_requests = set()
        self.automatic_activation_disabled = CMFlagFile('automatic_activation_disabled')
        self.changemonitor = changemonitor
        self.activationstate_handler = activationstate_handler
        self.snapshot = cmsnapshot.CMSnapshot(snapshot_handler)

    def reboot_request(self, node_name):
        logging.debug('reboot_request called for %s', node_name)

        self.reboot_requests.add(node_name)

    def _clear_reboot_requests(self):
        logging.debug('_clear_reboot_requests called')

        self.reboot_requests.clear()

    def _raise_reboot_alarms(self):
        logging.debug('_raise_reboot_alarms called')

        reboot_request_alarm = cmalarm.CMRebootRequestAlarm()

        for node_name in self.reboot_requests:
            reboot_request_alarm.raise_alarm_for_node(node_name)

    def get_property(self, prop_name, snapshot_name=None):
        logging.debug('get_property called for %s', prop_name)

        with self.lock.reader():
            if snapshot_name:
                self.snapshot.load(snapshot_name)

                return self.snapshot.get_property(prop_name)

            return self.backend_handler.get_property(prop_name)

    def get_properties(self, prop_filter, snapshot_name=None):
        logging.debug('get_properties  called with filter %s', prop_filter)

        with self.lock.reader():
            if snapshot_name:
                self.snapshot.load(snapshot_name)

                return self.snapshot.get_properties(prop_filter)

            return self.backend_handler.get_properties(prop_filter)

    def set_property(self, prop_name, prop_value):
        logging.debug('set_property called %s=%s', prop_name, prop_value)

        props = {}
        props[prop_name] = prop_value
        return self.set_properties(props)

    def set_properties(self, props, overwrite=False):
        logging.debug('set_properties called for %s', str(props))

        with self.lock.writer():
            self._validate_set(props)
            if overwrite:
                logging.debug('Deleting old configuration data as requested')
                orig_props = self.backend_handler.get_properties('.*')
                self.backend_handler.delete_properties(orig_props.keys())
            self.backend_handler.set_properties(props)
            self.csn.increment()

        if not self.automatic_activation_disabled:
            return self._activate_set(props)

        return "0"

    def delete_property(self, prop_name):
        logging.debug('delete_property called for %s', prop_name)

        props = []
        props.append(prop_name)
        return self._delete_properties(props, None)

    def delete_properties(self, arg):
        logging.debug('delete_properties called with arg %r', arg)

        keys = []
        prop_filter = None
        if isinstance(arg, str):
            prop_filter = arg
            props = self.get_properties(prop_filter)
            keys = props.keys()
        else:
            keys = arg
        return self._delete_properties(keys, prop_filter)

    def _delete_properties(self, props, props_filter):
        logging.debug('_delete_properties called with props %s filter %s', props, props_filter)

        with self.lock.writer():
            self._validate_delete(props)
            if props_filter:
                self.backend_handler.delete_properties(props_filter)
            else:
                if len(props) == 1:
                    self.backend_handler.delete_property(props[0])
                else:
                    self.backend_handler.delete_properties(props)
            self.csn.increment()

        if not self.automatic_activation_disabled:
            return self._activate_delete(props)

        return "0"

    def _validate_set(self, props):
        logging.debug('_validate_set called for %s', str(props))

        self.validator.validate_set(props)

    def _activate_set_no_lock(self, props):
        logging.debug('_activate_set_no_lock called for %s', str(props))

        uuid_value = self.changemonitor.start_change()

        work = cmactivationwork.CMActivationWork(cmactivationwork.CMActivationWork.OPER_SET,
                                                 self.csn.get(), props)
        work.uuid_value = uuid_value
        self.activator.add_work(work)
        return uuid_value

    def _activate_set(self, props):
        logging.debug('_activate_set called')

        with self.lock.reader():
            return self._activate_set_no_lock(props)

    def _validate_delete(self, props):
        logging.debug('_validate_delete called for %s', str(props))

        self.validator.validate_delete(props)

    def _activate_delete(self, props):
        logging.debug('_activate_delete called for %s', str(props))

        with self.lock.reader():
            uuid_value = self.changemonitor.start_change()
            work = cmactivationwork.CMActivationWork(cmactivationwork.CMActivationWork.OPER_DELETE,
                                                     self.csn.get(), props)
            work.uuid_value = uuid_value
            self.activator.add_work(work)
            return uuid_value

    def create_snapshot(self, snapshot_name):
        logging.debug('create_snapshot called, snapshot name is %s', snapshot_name)

        with self.lock.writer():
            self.snapshot.create(snapshot_name, self.backend_handler)

    def restore_snapshot(self, snapshot_name):
        logging.debug('restore_snapshot called, snapshot name is %s', snapshot_name)

        with self.lock.writer():
            self.snapshot.load(snapshot_name)

            self._validate_set(self.snapshot.get_properties())

            self.snapshot.restore(self.backend_handler)

            self.csn = cmcsn.CMCSN(self.backend_handler)

            self._activate_set_no_lock(self.snapshot.get_properties())

    def list_snapshots(self):
        logging.debug('list_snapshots called')

        snapshots = []
        with self.lock.writer():
            snapshots = self.snapshot.list()

        return snapshots

    def delete_snapshot(self, snapshot_name):
        logging.debug('delete_snapshot called, snapshot name is %s', snapshot_name)

        with self.lock.writer():
            self.snapshot.delete(snapshot_name)

    def activate(self, node_name=None, startup_activation=False):
        logging.debug('activate called, node is %s', node_name)

        activation_alarm = cmalarm.CMActivationFailedAlarm()
        if node_name:
            activation_alarm.cancel_alarm_for_node(node_name)
        else:
            activation_alarm.cancel_alarm_for_sg(CMProcessor.SERVICE_GROUP_NAME)

        with self.lock.reader():
            uuid_value = self.changemonitor.start_change()
            if not node_name:
                work = cmactivationwork.CMActivationWork(
                    cmactivationwork.CMActivationWork.OPER_FULL,
                    self.csn.get(), {}, None, startup_activation)
            else:
                work = cmactivationwork.CMActivationWork(
                    cmactivationwork.CMActivationWork.OPER_FULL,
                    self.csn.get(), {}, node_name)
            work.uuid_value = uuid_value
            self.activator.add_work(work)

        logging.debug('activation work added, going to wait for result')
        failures = work.get_result()
        logging.debug('got activation result')

        if self.reboot_requests:
            self._raise_reboot_alarms()

        if not node_name:
            self.activationstate_handler.clear_full_failed()

        if failures:
            logging.warning('Activation failed: %s', failures)

            failed_activators = [activator for handler in failures.keys()
                                 for activator in failures[handler]]

            supplementary_info = {'failed activators': failed_activators}

            if node_name:
                activation_alarm.raise_alarm_for_node(node_name, supplementary_info)
            else:
                self.activationstate_handler.set_full_failed(failed_activators)

                activation_alarm.raise_alarm_for_sg(CMProcessor.SERVICE_GROUP_NAME,
                                                    supplementary_info)
        return uuid_value

    def activate_node(self, node_name):
        logging.debug('activate_node called, node name is %s', node_name)

        if self.automatic_activation_disabled:
            return False

        with self.lock.reader():
            node_csn = self.csn.get_node_csn(node_name)

            if self.csn.get() == node_csn:
                logging.info('No change in data since last translation, last csn %d',
                             self.csn.get())
                return False

            self._clear_reboot_requests()
            work = cmactivationwork.CMActivationWork(cmactivationwork.CMActivationWork.OPER_NODE,
                                                     self.csn.get(), {}, node_name)
            self.activator.add_work(work)

        activation_alarm = cmalarm.CMActivationFailedAlarm()
        activation_alarm.cancel_alarm_for_node(node_name)

        failures = work.get_result()
        if failures:
            logging.warning('Activation failed: %s', failures)

            failed_activators = [activator for handler in failures.keys()
                                 for activator in failures[handler]]
            supplementary_info = {'failed activators': failed_activators}
            activation_alarm.raise_alarm_for_node(node_name, supplementary_info)

        else:
            with self.lock.writer():
                self.csn.sync_node_csn(node_name)

        return node_name in self.reboot_requests

    def set_automatic_activation_state(self, state):
        logging.debug('set_automatic_activation_state called, state is %s', state)

        with self.lock.writer():
            if state:
                self.automatic_activation_disabled.unset()
            else:
                self.automatic_activation_disabled.set()
