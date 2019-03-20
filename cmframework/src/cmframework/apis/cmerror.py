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
import sys


class CMError(Exception):
    def __init__(self, description):
        super(CMError, self).__init__(description)
        self.description = description

    def get_description(self):
        return self.description

    def __str__(self):
        return '%s' % self.description


if __name__ == '__main__':
    try:
        raise CMError(int(sys.argv[1]))
    except CMError as error:
        print('Got exception %s' % str(error))
    except Exception as exp:  # pylint: disable=broad-except
        print('Got exception %s' % str(exp))
