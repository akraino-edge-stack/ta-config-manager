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

from cmframework.apis import cmactivator
from cmframework.utils import cmactivationrmq
from cmframework.server import cmactivatehandler


class CMActivateRMQHandler(cmactivatehandler.CMActivateHandler):
    def __init__(self, rmq_host, rmq_port):
        self.rmq_host = rmq_host
        self.rmq_port = rmq_port
        self.rmq_publisher = cmactivationrmq.CMActivationRMQPublisher(self.rmq_host, self.rmq_port)

    def activate(self, work):
        logging.debug('CMAcivateRMQHandler activating %s', work)
        self.rmq_publisher.send(work)

    def is_supported(self, activator_plugin):
        return isinstance(activator_plugin, cmactivator.CMLocalActivator)
