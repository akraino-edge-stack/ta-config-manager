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
import logging
import pika

from cmframework.apis import cmerror
from cmframework.utils import cmactivationwork


class CMActivationRMQ(object):
    EXCHANGE = 'cmframework.activator'

    def __init__(self, host, port):
        try:
            self.host = host
            self.port = port
            self.connection = pika.BlockingConnection(
                pika.ConnectionParameters(host=self.host, port=self.port))
            self.channel = self.connection.channel()
            self.channel.exchange_declare(exchange=CMActivationRMQ.EXCHANGE, type='direct')
        except Exception as exp:  # pylint: disable=broad-except
            raise cmerror.CMError(str(exp))


class CMActivationRMQPublisher(CMActivationRMQ):
    def __init__(self, host, port):
        CMActivationRMQ.__init__(self, host, port)

    def send(self, work):
        try:
            data = work.serialize()
            self.channel.basic_publish(exchange=CMActivationRMQ.EXCHANGE,
                                       routing_key=work.get_target(),
                                       body=data)
            logging.debug('Sent %s to activation exchange', str(work))
        except Exception as exp:  # pylint: disable=broad-except
            self.connection.close()
            raise cmerror.CMError(str(exp))


class CMActivationRMQConsumer(CMActivationRMQ):
    class WorkConsumer(object):
        # pylint: disable=no-self-use, unused-argument
        def consume(self, work):
            raise cmerror.CMError('Not implemented')

    def __init__(self, host, port, consumer, node):
        CMActivationRMQ.__init__(self, host, port)
        self.node = node
        result = self.channel.queue_declare(exclusive=True)
        self.queue_name = result.method.queue
        self.channel.queue_bind(exchange=CMActivationRMQ.EXCHANGE, queue=self.queue_name,
                                routing_key=node)
        self.channel.queue_bind(exchange=CMActivationRMQ.EXCHANGE, queue=self.queue_name,
                                routing_key='all')
        self.channel.basic_consume(self,
                                   queue=self.queue_name,
                                   no_ack=True)
        self.consumer = consumer

    def __call__(self, ch, method, properties, body):
        logging.debug('Received %r', body)
        work = cmactivationwork.CMActivationWork()
        work.deserialize(body)
        self.consumer.consume(work)

    def receive(self):
        try:
            self.channel.start_consuming()
        except Exception as exp:  # pylint: disable=broad-except
            self.connection.close()
            raise cmerror.CMError(str(exp))


def main():
    import sys
    import argparse

    class MyConsumer(CMActivationRMQConsumer.WorkConsumer):
        def consume(self, work):
            print('Got work %s' % work)

    parser = argparse.ArgumentParser(description='Test rabbitmq activator', prog=sys.argv[0])
    parser.add_argument('--role', required=True, action='store')
    parser.add_argument('--host', required=True, action='store')
    parser.add_argument('--port', required=True, type=int, action='store')
    parser.add_argument('--operation', required=False, type=int, action='store')
    parser.add_argument('--csn', required=False, type=int, action='store')
    parser.add_argument('--node', required=True, type=str, action='store')
    parser.add_argument('--properties', required=False, nargs=2, action='append')
    args = parser.parse_args(sys.argv[1:])
    if args.role == 'publisher':
        if not args.operation or not args.csn or not args.properties:
            print('Missing options')
            sys.exit(1)
        publisher = CMActivationRMQPublisher(args.host, args.port)
        props = {}
        for prop in args.properties:
            props[prop[0]] = prop[1]
        work = cmactivationwork.CMActivationWork(args.operation, args.csn, props)
        publisher.send(work)
    elif args.role == 'consumer':
        myconsumer = MyConsumer()
        consumer = CMActivationRMQConsumer(args.host, args.port, myconsumer, args.node)
        consumer.receive()
    else:
        print('Invalid role %s' % args.role)
        sys.exit(1)


if __name__ == '__main__':
    main()
