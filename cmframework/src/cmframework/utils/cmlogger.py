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
import re
import sys
import logging
from logging.handlers import SysLogHandler

from cmframework.apis import cmerror


class CMMaskFormatter(object):
    def __init__(self, orig_formatter, patterns):
        self.orig_formatter = orig_formatter
        self.patterns = patterns

    def format(self, record):
        msg = self.orig_formatter.format(record)
        regex = r'([\\]*\"{}[\\]*\":\s[\\]*\")[^\"\\\s]+([\\]*\")'
        for pattern in self.patterns:

            msg = re.sub(regex.format(pattern),
                         r'\1*** password ***\2', msg)

        return msg

    def __getattr__(self, attr):
        return getattr(self.orig_formatter, attr)


class CMLogger(object):
    levels = {'debug': logging.DEBUG,
              'info': logging.INFO,
              'warning': logging.WARNING,
              'error': logging.error}

    DEST_CONSOLE = 1
    DEST_SYSLOG = 2
    dests = {'console': DEST_CONSOLE,
             'syslog': DEST_SYSLOG}

    def __init__(self, dest, verbose, level, mask_names=None):
        self.verbose = verbose
        self.dest = dest
        self.level = level
        self.formatter = None
        self.handler = None
        self.mask_formatter = None
        if mask_names is None:
            mask_names = []
        self.init(mask_names)

    def init(self, mask_names):
        if self.level not in CMLogger.levels.values():
            raise cmerror.CMError('Invalid level value, possible values are %s' %
                                  str(CMLogger.levels))

        if self.dest not in CMLogger.dests.values():
            raise cmerror.CMError('Invalid destination value, possible values are %s' %
                                  str(CMLogger.dests))

        if self.verbose:
            if self.dest is CMLogger.DEST_CONSOLE:
                format_str = '[%(asctime)s %(levelname)7s %(module)s(%(lineno)3s)] %(message)s'
            else:
                format_str = '[%(module)s(%(lineno)3s)] %(message)s'
        else:
            format_str = '%(message)s'

        self.formatter = logging.Formatter(format_str)
        self.mask_formatter = CMMaskFormatter(self.formatter, mask_names)
        self.set_dest(self.dest)

        logging.getLogger().setLevel(self.level)

    def set_level(self, level):
        self.level = level
        logging.getLogger().setLevel(self.level)

    def set_dest(self, dest):
        if self.dest != dest or self.handler is None:
            if self.handler:
                logging.getLogger().removeHandler(self.handler)

            if self.dest is CMLogger.DEST_CONSOLE:
                self.handler = logging.StreamHandler(sys.stdout)
                self.handler.setFormatter(self.mask_formatter)
            elif self.dest is CMLogger.DEST_SYSLOG:
                print '====> setting destination to syslog'
                self.handler = SysLogHandler(address='/dev/log')
                self.handler.setFormatter(self.mask_formatter)
            logging.getLogger().addHandler(self.handler)

    @staticmethod
    def str_to_level(level):
        ret = None
        try:
            ret = CMLogger.levels[level]
        except KeyError:
            raise cmerror.CMError('Invalid log level, possible values %s' %
                                  str(CMLogger.levels.keys()))
        return ret

    @staticmethod
    def str_to_dest(dest):
        ret = None
        try:
            ret = CMLogger.dests[dest]
        except KeyError:
            raise cmerror.CMError('Invalid destination, possible values %s' %
                                  str(CMLogger.dests.keys()))
        return ret

    @staticmethod
    def level_to_str(level):
        for key, value in CMLogger.levels.iteritems():
            if value is level:
                return key
        return None

    @staticmethod
    def dest_to_str(dest):
        for key, value in CMLogger.dests.iteritems():
            if value is dest:
                return key
        return None


def main():
    log_dest = CMLogger.str_to_dest('console')
    log_level = CMLogger.str_to_level('debug')
    _ = CMLogger(log_dest, True, log_level)
    world = 'world'
    logging.error('hello %s!', world)
    logging.warn('hello %s!', world)
    logging.info('hello %s!', world)
    logging.debug('hello %s!', world)


if __name__ == '__main__':
    main()
