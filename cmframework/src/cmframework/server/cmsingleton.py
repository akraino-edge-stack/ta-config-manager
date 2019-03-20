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


class _CMSingleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(_CMSingleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class CMSingleton(_CMSingleton('SingletonMeta', (object,), {})):
    pass


def main():
    class TestSingleton(CMSingleton):
        def __init__(self):
            self.counter = 0

        def inc(self):
            self.counter += 1

        def dec(self):
            self.counter -= 1

        def __str__(self):
            return 'Counter now is %d' % self.counter

    instance1 = TestSingleton()
    instance1.inc()
    instance2 = TestSingleton()
    instance2.inc()
    print str(instance2)


if __name__ == '__main__':
    main()
