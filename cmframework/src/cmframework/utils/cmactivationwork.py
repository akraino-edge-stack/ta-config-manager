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
from threading import Condition
import json

from cmframework.apis import cmerror


class CMActivationWork(object):
    """
    Serialize/Deserialize the work to/from json, the structure of the json data is the following:
    {
        'operation': <operation number>,
        'csn': <csn number>,
        'properties': {
            '<name>': '<value>',
            ....
        }
    }
    """

    OPER_NONE = 0
    OPER_SET = 1
    OPER_DELETE = 2
    OPER_FULL = 3
    OPER_NODE = 4

    OPER_NAMES = ('NONE', 'SET', 'DELETE', 'FULL', 'NODE')

    def __init__(self,
                 operation=OPER_NONE,
                 csn=0,
                 props=None,
                 target=None,
                 startup_activation=False):
        self.operation = operation
        self.csn = csn
        if not props:
            self.props = {}
        else:
            self.props = props
        self.target = target
        self.condition = Condition()
        self.condition.acquire()
        self.result = None
        self.uuid_value = None
        self.startup_activation = startup_activation

    def __str__(self):
        return '(%r %d %r %r %r)' % (self._get_operation_name(),
                                     self.csn,
                                     self.props,
                                     self.target,
                                     self.startup_activation)

    def _get_operation_name(self):
        return CMActivationWork.OPER_NAMES[self.operation]

    def get_operation(self):
        return self.operation

    def get_csn(self):
        return self.csn

    def get_props(self):
        return self.props

    def get_target(self):
        return self.target

    def add_result(self, result):
        self.condition.acquire()
        self.result = result
        self.condition.notify()
        self.condition.release()

    def get_result(self):
        self.condition.acquire()
        self.condition.wait()
        self.condition.release()
        return self.result

    def release(self):
        self.condition.notify()
        self.condition.release()

    def is_startup_activation(self):
        return self.startup_activation

    def serialize(self):
        try:
            data = {}
            data['operation'] = self.operation
            data['csn'] = self.csn
            data['properties'] = self.props
            data['result'] = self.result
            data['startup_activation'] = self.startup_activation
            return json.dumps(data)
        except Exception as exp:
            raise cmerror.CMError(str(exp))

    def deserialize(self, msg):
        try:
            data = json.loads(msg)
            self.operation = data['operation']
            self.csn = data['csn']
            self.props = data['properties']
            self.result = data['result']
            self.startup_activation = data['startup_activation']
        except Exception as exp:
            raise cmerror.CMError(str(exp))


if __name__ == '__main__':
    work = CMActivationWork(CMActivationWork.OPER_FULL, 10, {})
    print 'Work is %s' % work
