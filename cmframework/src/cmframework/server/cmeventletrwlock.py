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
from __future__ import print_function
from eventlet import greenthread, hubs


class CMEventletRWLock(object):
    def __init__(self):
        self.counter = 0
        self._read_waiters = set()
        self._write_waiters = set()

    def reader(self):
        return self.Reader(self)

    def writer(self):
        return self.Writer(self)

    class Base(object):
        def __init__(self, parent):
            self.parent = parent

        def _acquire(self, waiters):
            waiters.add(greenthread.getcurrent())

            try:
                while self.parent.counter != 0:
                    hubs.get_hub().switch()
            finally:
                waiters.discard(greenthread.getcurrent())

        def _exit(self):
            for waiters, fn in (
                    (self.parent._read_waiters, lambda x: x >= 0),
                    (self.parent._write_waiters, lambda x: x == 0),
            ):
                if not waiters:
                    continue

                hubs.get_hub().schedule_call_global(
                    0, self._release, waiters, fn,
                )

        def _release(self, waiters, fn):
            if waiters and fn(self.parent.counter):
                waiters.pop().switch()

    class Reader(Base):
        def __enter__(self):
            if self.parent.counter < 0:
                self._acquire(self.parent._read_waiters)
            self.parent.counter += 1

        def __exit__(self, *args, **kwargs):
            self.parent.counter -= 1
            self._exit()

    class Writer(Base):
        def __enter__(self):
            if self.parent.counter != 0:
                self._acquire(self.parent._write_waiters)
            self.parent.counter -= 1

        def __exit__(self, *args, **kwargs):
            self.parent.counter += 1
            self._exit()


def main():
    lock = CMEventletRWLock()
    with lock.reader():
        print('Got reader lock')

    with lock.writer():
        print('Got write lock')


if __name__ == '__main__':
    main()
