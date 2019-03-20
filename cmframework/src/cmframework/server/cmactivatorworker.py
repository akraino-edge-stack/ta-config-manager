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
from threading import Thread


class CMActivatorWorker(Thread):
    def __init__(self, activator, index, lock, parallel=False):
        super(CMActivatorWorker, self).__init__()

        self.activator = activator
        self.index = index
        self.lock = lock
        self.parallel = parallel

        self.daemon = True

    def __str__(self):
        return 'worker-{}'.format(self.index)

    def _handle_work(self, work):
        logging.debug('%s handling work: %s', self, work)
        failures = {}
        for handler in self.activator.get_handlers():
            try:
                logging.info('%s activating using %s', self, handler.__class__.__name__)
                handler_failures = handler.activate(work)
                if handler_failures:
                    logging.error('%s activation failed, error count=%s',
                                  self,
                                  len(handler_failures))
                    failures[handler.__class__.__name__] = handler_failures
            except Exception as exp:  # pylint: disable=broad-except
                logging.error('%s activation failed with error %s', self, str(exp))
                failures[handler.__class__.__name__] = str(exp)

        logging.debug('%s handled work: %s', self, work)

        work.add_result(failures)

    def run(self):
        while True:
            if self.parallel:
                work = self.activator.get_parallel_work()
                with self.lock.reader():
                    self._handle_work(work)
            else:
                work = self.activator.get_work()
                with self.lock.writer():
                    self._handle_work(work)
