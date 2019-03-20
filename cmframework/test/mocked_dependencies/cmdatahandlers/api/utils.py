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


def is_virtualized():
    return False


def get_own_hwmgmt_ip():
    return '1.2.3.4'


def flatten_config_data(jsondata):
    result = {}
    for key, value in jsondata.iteritems():
        try:
            result[key] = json.dumps(value)
        except Exception as exp:
            result[key] = value
    return result


def unflatten_config_data(props):
    propsjson = {}
    for name, value in props.iteritems():
        try:
            propsjson[name] = json.loads(value)
        except Exception as exp:
            propsjson[name] = value
    return propsjson
