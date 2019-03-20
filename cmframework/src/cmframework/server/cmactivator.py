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
from Queue import Queue

from cmframework.server import cmeventletrwlock
from cmframework.server import cmactivatorworker


class CMActivator(object):
    def __init__(self, worker_count):
        self.works = Queue()
        self.node_works = Queue()
        self.handlers = []
        self.workers = []
        self.worker_count = worker_count
        self.lock = cmeventletrwlock.CMEventletRWLock()

    def add_handler(self, handler):
        self.handlers.append(handler)

    def get_parallel_work(self):
        return self.node_works.get()

    def get_work(self):
        return self.works.get()

    def add_work(self, work):
        work.release()
        if not work.get_target():
            self.works.put(work)
        else:
            self.node_works.put(work)

    def get_handlers(self):
        return self.handlers

    def start(self):
        worker = cmactivatorworker.CMActivatorWorker(self, 0, self.lock)
        worker.start()
        self.workers.append(worker)

        for i in range(1, self.worker_count+1):
            worker = cmactivatorworker.CMActivatorWorker(self, i, self.lock, parallel=True)
            worker.start()
            self.workers.append(worker)
