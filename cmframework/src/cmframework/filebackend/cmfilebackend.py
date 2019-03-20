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
import re
import os
import stat

from cmframework.apis import cmbackend
from cmframework.apis import cmerror


class CMFileBackend(cmbackend.CMBackend):
    def __init__(self, **kw):
        self.uri = kw['uri']
        logging.debug('CMFileBackend constructor called, uri=%s', self.uri)
        self.data = {}
        self.load_file()

    def load_file(self):
        logging.debug('load_file started')
        try:
            self.data = {}
            with open(self.uri) as f:
                lines = f.read().splitlines()
                for line in lines:
                    name, var = line.partition('=')[::2]
                    logging.debug('Adding %s=%s', name, var)
                    self.data[name.strip()] = var
                f.close()
        except IOError:
            logging.debug('File %s does not exist', self.uri)

    def write_file(self):
        logging.debug('write_file started')
        try:
            with open(self.uri, 'w') as f:
                os.chmod(self.uri, stat.S_IRUSR | stat.S_IWUSR)
                for key, value in self.data.iteritems():
                    logging.debug('Writing %s=%s', key, value)
                    f.write(key + '=' + value + '\n')
                f.flush()
                os.fsync(f.fileno())
        except IOError as exp:
            raise cmerror.CMError(str(exp))

    def get_property(self, prop_name):
        logging.debug('get_property called for %s', prop_name)
        try:
            value = self.data[prop_name]
            return value
        except KeyError:
            raise cmerror.CMError('Invalid property name')

    def get_properties(self, prop_filter):
        logging.debug('get_properties called with filter %s', prop_filter)
        returned = {}
        pattern = re.compile(prop_filter)
        for key, value in self.data.iteritems():
            logging.debug('Matching %s against %s', key, prop_filter)
            if pattern.match(key):
                logging.debug('Adding %s', key)
                returned[key] = value
        return returned

    def set_property(self, prop_name, prop_value):
        logging.debug('set_property %s=%s', prop_name, prop_value)
        props = {}
        props[prop_name] = prop_value
        self.set_properties(props)

    def set_properties(self, properties):
        logging.debug('set_properties called props=%s', str(properties))
        try:
            for key, value in properties.iteritems():
                self.data[key] = value
            self.write_file()
        except cmerror.CMError:
            self.load_file()
            raise

    def delete_property(self, prop_name):
        logging.debug('delete_property called for %s', prop_name)
        try:
            del self.data[prop_name]
            self.write_file()
        except KeyError:
            logging.debug('Property not found')
            raise cmerror.CMError('Property not found')
        except cmerror.CMError:
            self.load_file()
            raise

    def delete_properties(self, arg):
        logging.debug('delete_properties called with arg %s', arg)
        try:
            if isinstance(arg, str):
                pattern = re.compile(arg)
                for key in self.data.keys():  # pylint: disable=consider-iterating-dictionary
                    if pattern.match(key):
                        del self.data[key]
            else:
                for prop in arg:
                    for key in self.data.keys():  # pylint: disable=consider-iterating-dictionary
                        if key == prop:
                            del self.data[key]
            self.write_file()
        except cmerror.CMError:
            self.load_file()
            raise


def main():
    import sys

    filepath = sys.argv[1]
    try:
        print('Initializing backend at %s' % filepath)
        filebackend = CMFileBackend(uri=filepath)
        print('Adding key1=value1')
        filebackend.set_property("key1", "value1")
        properties = {'key2': 'value2', 'key3': 'value3'}
        print('Adding %s' % str(properties))
        filebackend.set_properties(properties)
        print('Getting key1')
        value = filebackend.get_property('key1')
        print('value of key1 is %s' % value)
        print('Deleting key2')
        filebackend.delete_property('key2')
        print('Getting *')
        properties = filebackend.get_properties('.*')
        print('Got %s' % str(properties))
        print('Delete all properties')
        filebackend.delete_properties('.*')
    except cmerror.CMError as exp:
        print('Got exeption %s' % str(exp))
        sys.exit(1)


if __name__ == '__main__':
    main()
