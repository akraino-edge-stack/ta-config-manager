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
from cmframework.apis import cmerror


class CMState(object):
    # pylint: disable=no-self-use, unused-argument
    def get(self, domain, name):
        raise cmerror.CMError('No implemented')

    # pylint: disable=no-self-use, unused-argument
    def get_domain(self, domain):
        raise cmerror.CMError('Not implemented')

    # pylint: disable=no-self-use, unused-argument
    def set(self, domain, name, value):
        raise cmerror.CMError('Not implemented')

    # pylint: disable=no-self-use, unused-argument
    def get_domains(self):
        raise cmerror.CMError('Not implemented')

    # pylint: disable=no-self-use, unused-argument
    def delete(self, domain, name):
        raise cmerror.CMError('Not implemented')

    # pylint: disable=no-self-use, unused-argument
    def delete_domain(self, domain):
        raise cmerror.CMError('Not implemented')

if __name__ == '__main__':
    pass
