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
from Queue import Queue
from threading import Thread

from cmframework.server.cmsingleton import CMSingleton
from cmframework.utils.cmalarmwork import CMAlarmWork
from cmframework.apis import cmerror


class AlarmHandler(Thread, CMSingleton):
    def __init__(self):
        super(AlarmHandler, self).__init__()

        self.handler_lib = None
        self.works = Queue()

        self.daemon = True

    def set_library_impl(self, handler_lib_impl_module, **kw):
        try:
            logging.debug('Loading alarmhandler lib from %s', handler_lib_impl_module)
            # Separate class path and module name
            parts = handler_lib_impl_module.rsplit('.', 1)
            module_path = parts[0]
            class_name = parts[1]
            logging.debug('Importing %s from %s', class_name, module_path)
            module = __import__(module_path, fromlist=[module_path])
            classobj = getattr(module, class_name)
            logging.debug('Constructing alarm handler lib with args %r', kw)
            self.handler_lib = classobj(**kw)
        except ImportError as exp1:
            raise cmerror.CMError(str(exp1))
        except Exception as exp2:  # pylint: disable=broad-except
            raise cmerror.CMError(str(exp2))

    def cancel_alarm_with_dn(self,
                             alarm_id,
                             dn,
                             supplementary_info):
        logging.debug('AlarmHandler.cancel_alarm_with_dn called')

        alarmwork = CMAlarmWork(CMAlarmWork.OPER_CANCEL, alarm_id, dn, supplementary_info)

        self._add_work(alarmwork)

    def raise_alarm_with_dn(self,
                            alarm_id,
                            dn,
                            supplementary_info):
        logging.debug('AlarmHandler.raise_alarm_with_dn called')

        alarmwork = CMAlarmWork(CMAlarmWork.OPER_RAISE, alarm_id, dn, supplementary_info)

        self._add_work(alarmwork)

    def _get_work(self):
        return self.works.get()

    def _add_work(self, work):
        logging.debug('AlarmHandler._add_work called with %s', work)

        self.works.put(work)

    def run(self):
        while True:
            work = self._get_work()
            if self.handler_lib:
                logging.debug('Asking handler lib to handle work: %s', work)
                self.handler_lib.handle_alarm_work(work)
                logging.debug('Handler lib handled work: %s', work)
            else:
                logging.warning('No handler lib set to handle work')
