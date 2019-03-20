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
import json
import logging

from cmframework.server.cmhttperrors import CMHTTPErrors
from cmframework.server import cmrestapiv1


class CMRestAPIFactory(object):
    def __init__(self, processor, base_url):
        self.apis = {}
        api = cmrestapiv1.CMRestAPIV1(processor)
        self.apis[api.get_version()] = api
        self.base_url = base_url

    def get_apis(self, rpc):
        """
            Request: GET http://<cm-vip:port>/cm/apis
            Response:
                {
                    "versions": [
                        {
                            "id": "<version>",
                            "href": "<http address for the api>"
                            "min-version": "<mimimum version required to support this version>",
                            "status": "<supported|deprecated|unsupported|current>"
                        },
                        ...
                    ]
                }
        """
        try:
            logging.debug('get_apis called')
            reply = {}
            versions = []
            for key, value in self.apis.iteritems():
                version = {}
                version['id'] = value.get_version()
                version['href'] = '%s%s/' % (self.base_url, key)
                version['min-version'] = value.get_minimum_version()
                version['status'] = value.get_status()
                versions.append(version)
            reply['versions'] = versions
            rpc.rep_status = CMHTTPErrors.get_ok_status()
            rpc.rep_body = json.dumps(reply)
            logging.debug('returning, rpc=%s', str(rpc))
        except Exception as exp:  # pylint: disable=broad-except
            logging.error('Got exception %s', str(exp))
            rpc.rep_status = CMHTTPErrors.get_internal_error_status()
            rpc.rep_status += ','
            rpc.rep_status += str(exp)

    def get_api(self, version):
        logging.debug('get_api called with version %s', version)
        api = None
        try:
            api = self.apis[version]
        except KeyError:
            logging.warn('Could not find API with version %s', version)
        return api


if __name__ == '__main__':
    rest_api_factory = CMRestAPIFactory(None, None)
