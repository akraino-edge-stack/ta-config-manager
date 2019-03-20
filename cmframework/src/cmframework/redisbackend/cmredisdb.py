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
# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4
from __future__ import print_function
from urlparse import urlparse
import re
import time
import functools
import redis

from cmframework.apis import cmerror
from cmframework.apis import cmbackend


def retry(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        for _ in xrange(20):
            try:
                return func(*args, **kwargs)
            except Exception, e:  # pylint: disable=broad-except
                time.sleep(1)
                retExc = e
        raise retExc

    return wrapper


class CMRedisDB(cmbackend.CMBackend):

    def __init__(self, **kw):
        dburl = kw['uri']
        urldata = urlparse(dburl)
        self.vip = urldata.hostname
        self.port = urldata.port
        self.password = urldata.password
        self.client = redis.StrictRedis(host=self.vip, port=self.port, password=self.password)

    @retry
    def set_property(self, prop_name, prop_value):
        self.client.set(prop_name, prop_value)

    def get_property(self, prop_name):
        return self.client.get(prop_name)

    @retry
    def delete_property(self, prop_name):
        self.client.delete(prop_name)

    @retry
    def set_properties(self, properties):
        pipe = self.client.pipeline()
        for name, value in properties.iteritems():
            pipe.set(name, value)
        pipe.execute()

    def get_properties(self, prop_filter):
        # seems redis does not understand regex, it understands only glob
        # patterns, thus we need to handle the matching by ourselves :/
        keys = self.client.keys()
        pattern = re.compile(prop_filter)
        props = {}
        for key in keys:
            if pattern.match(key):
                value = self.client.get(key)
                props[key] = value
        return props

    @retry
    def delete_properties(self, arg):
        if not isinstance(arg, list):
            raise cmerror.CMError('Deleting with filter is not supported by the backend')
        pipe = self.client.pipeline()
        for prop in arg:
            pipe.delete(prop)
        pipe.execute()


def main():
    import argparse
    import sys
    import traceback

    parser = argparse.ArgumentParser(description='Test redis db plugin', prog=sys.argv[0])

    parser.add_argument('--uri',
                        required=True,
                        dest='uri',
                        metavar='URI',
                        help='The redis db uri format redis://:password@<ip>:port',
                        type=str,
                        action='store')

    parser.add_argument('--api',
                        required=True,
                        dest='api',
                        metavar='API',
                        help=('The api name, can be set_property, get_property, delete_property, '
                              'set_properties, get_properties, delete_properties'),
                        type=str,
                        action='store')

    parser.add_argument('--property',
                        required=False,
                        dest='properties',
                        metavar='PROPERTY',
                        help='The property in the format name[=value]',
                        type=str,
                        action='append')

    parser.add_argument('--filter',
                        required=False,
                        dest='filter',
                        metavar='FILTER',
                        help='The regular expression matching the property names',
                        type=str,
                        action='store')

    args = parser.parse_args(sys.argv[1:])

    try:
        uri = args.uri
        api = args.api
        p = {}
        p['uri'] = uri
        db = CMRedisDB(**p)
        print('Involing %s' % api)
        func = getattr(db, api)
        if api == 'set_property':
            if not args.properties:
                raise Exception('Missing --properties argument')
            for prop in args.properties:
                i = prop.index('=')
                name = prop[:i]
                value = prop[(i + 1):]
                print("Setting %s to %s" % (name, value))
                func(name, value)
        elif api == 'get_property':
            if not args.properties:
                raise Exception('Missing --properties argument')
            for prop in args.properties:
                value = func(prop)
                print('%s=%s' % (prop, value))
        elif api == 'delete_property':
            if not args.properties:
                raise Exception('Missing --properties argument')
            for prop in args.properties:
                print('Deleting %s' % prop)
                func(prop)
        elif api == 'set_properties':
            if not args.properties:
                raise Exception('Missing --properties argument')
            props = {}
            for prop in args.properties:
                i = prop.index('=')
                name = prop[:i]
                value = prop[(i + 1):]
                props[name] = value
            func(props)
        elif api == 'get_properties':
            if not args.filter:
                raise Exception('Missing --filter argument')
            print('Getting properties matching %s' % args.filter)
            props = func(args.filter)
            for key, value in props.iteritems():
                print('%s=%s' % (key, value))
        elif api == 'delete_properties':
            if not args.properties:
                raise Exception('Missing --properties argument')
            func(args.properties)
    except Exception as exp:  # pylint: disable=broad-except
        print('Failed with error %s', exp)
        traceback.print_exc()
        sys.exit(1)
    sys.exit(0)


if __name__ == '__main__':
    main()
