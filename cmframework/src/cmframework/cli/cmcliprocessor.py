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
import argparse

from cmframework.apis import cmerror
from cmframework.cli import cmclihandlers


class CMCLIProcessor(object):
    def __init__(self, prog):
        self.prog = prog

    def __call__(self, args):
        parser = argparse.ArgumentParser(description='Configuration Management CLI', prog=self.prog)
        parser.add_argument('--ip',
                            dest='ip',
                            metavar='SERVER-IP',
                            default='config-manager',
                            type=str,
                            action='store')

        parser.add_argument('--port',
                            dest='port',
                            metavar='SERVER-PORT',
                            default=61100,
                            type=int,
                            action='store')

        parser.add_argument('--client-lib',
                            dest='client_lib',
                            metavar='CLIENT-LIB',
                            default='cmframework.lib.CMClientImpl',
                            type=str,
                            action='store')

        parser.add_argument('--verbose',
                            required=False,
                            default=False,
                            action='store_true')

        subparsers = parser.add_subparsers()
        handlers = cmclihandlers.get_handlers_list()
        for handler in handlers:
            handler.init_subparser(subparsers)

        parse_result = parser.parse_args(args)

        try:
            parse_result.handler(parse_result)
        except cmerror.CMError:
            raise
        except Exception as exp:
            raise cmerror.CMError(str(exp))


def main():
    processor = CMCLIProcessor('cmcli')
    args = sys.argv[1:]
    try:
        processor(args)
    except cmerror.CMError as error:
        print('Got error %s' % str(error))
        sys.exit(1)


if __name__ == '__main__':
    main()
