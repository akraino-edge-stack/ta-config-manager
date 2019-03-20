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

from cmframework.utils.cmalarmhandler import AlarmHandler


class CMAlarm(object):
    NODE_REBOOT_REQUEST_ALARM = '45001'
    ACTIVATION_FAILED_ALARM = '45002'

    def _get_alarm_id(self):
        raise NotImplementedError('Not implemented alarm')

    def raise_alarm_for_node(self, node_name, supplementary_info=None):
        logging.debug('raise_alarm_for_node called with %s %s', node_name, supplementary_info)

        self._raise_alarm_with_dn('NODE-{}'.format(node_name), supplementary_info)

    def raise_alarm_for_sg(self, sg_name, supplementary_info=None):
        logging.debug('raise_alarm_for_sg called with %s %s', sg_name, supplementary_info)

        self._raise_alarm_with_dn('SG-{}'.format(sg_name), supplementary_info)

    def _raise_alarm_with_dn(self, dn, supplementary_info=None):
        logging.debug('raise_alarm called for %s with %s %s',
                      self._get_alarm_id(),
                      dn,
                      supplementary_info)

        if not supplementary_info:
            supplementary_info = {}

        try:
            alarm_handler = AlarmHandler()

            alarm_handler.raise_alarm_with_dn(self._get_alarm_id(),
                                              dn,
                                              supplementary_info)
        except Exception as ex:  # pylint: disable=broad-except
            logging.warning('Alarm raising failed: %s', str(ex))

    def cancel_alarm_for_node(self, node_name, supplementary_info=None):
        logging.debug('cancel_alarm called with %s %s', node_name, supplementary_info)

        self._cancel_alarm_with_dn('NODE-{}'.format(node_name), supplementary_info)

    def cancel_alarm_for_sg(self, sg_name, supplementary_info=None):
        logging.debug('cancel_alarm called with %s %s', sg_name, supplementary_info)

        self._cancel_alarm_with_dn('SG-{}'.format(sg_name), supplementary_info)

    def _cancel_alarm_with_dn(self, dn, supplementary_info=None):
        logging.debug('cancel_alarm called for %s with %s %s',
                      self._get_alarm_id(),
                      dn,
                      supplementary_info)

        if not supplementary_info:
            supplementary_info = {}

        try:
            alarm_handler = AlarmHandler()

            alarm_handler.cancel_alarm_with_dn(self._get_alarm_id(),
                                               dn,
                                               supplementary_info)
        except Exception as ex:  # pylint: disable=broad-except
            logging.warning('Alarm canceling failed: %s', str(ex))


class CMRebootRequestAlarm(CMAlarm):
    def _get_alarm_id(self):
        return CMAlarm.NODE_REBOOT_REQUEST_ALARM


class CMActivationFailedAlarm(CMAlarm):
    def _get_alarm_id(self):
        return CMAlarm.ACTIVATION_FAILED_ALARM
