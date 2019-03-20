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


class HTTPRPC(object):
    def __init__(self):
        self.req_body = ''
        self.req_filter = ''
        self.req_params = {}
        self.req_method = ''
        self.rep_body = ''
        self.rep_status = ''

    def __str__(self):
        return str.format('REQ: body:{body} filter:{filter} '
                          'params:{params} method:{method} '
                          'REP: body:{rep_body} status:{status}',
                          body=self.req_body, filter=self.req_filter,
                          params=str(self.req_params), method=self.req_method,
                          rep_body=self.rep_body, status=self.rep_status)
