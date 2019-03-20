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
import os
import sys
import inspect
import imp
import types
import argparse

from cmdatahandlers.api import configerror

class ConfigManager(object):
    #This needs to be updated when new domain are introduced, a getter function
    #should be added to the domain config handler
    """
    def __init__(self, schema, configjson):
        #validate according to schema
        try:
            self.configjson = configjson
            builder = pjo.ObjectBuilder(schema)
            ns = builder.build_classes()
            self.config = ns.Config(**configjson)
            self._load_config_handlers()
        except Exception as exp:
            raise configerror.ConfigError(str(exp))
    """

    def __init__(self, configjson):
        #validate according to schema
        self.configmap = {}
        try:
            self.configjson = configjson
            self._load_config_handlers()
        except Exception as exp:
            raise configerror.ConfigError(str(exp))

    def get_config(self):
        return self.configjson

    def get_cloud_name(self):
        if 'cloud.name' not in self.configjson:
            raise configerror.ConfigError('Cloud name not defined')

        return self.configjson['cloud.name']

    def get_cloud_description(self):
        if 'cloud.description' not in self.configjson:
            raise configerror.ConfigError('Cloud description not defined')
        return self.configjson['cloud.description']

    def get_cloud_installation_date(self):
        if 'cloud.installation_date' not in self.configjson:
            raise configerror.ConfigError('Cloud installation date is not defined')
        return self.configjson['cloud.installation_date']

    def get_cloud_installation_phase(self):
        if 'cloud.installation_phase' not in self.configjson:
            raise configerror.ConfigError('Cloud installation phase is not defined')
        return self.configjson['cloud.installation_phase']

    def _load_config_handlers(self):
        myfolder = os.path.realpath(os.path.abspath(os.path.split(inspect.getfile(inspect.currentframe()))[0]))
        dirn = os.path.dirname(myfolder)
        basen = os.path.basename(myfolder)

        for d in os.listdir(dirn):
            if d == basen:
                continue
            if not os.path.isdir(dirn + '/' + d):
                continue

            configmodule = dirn + '/' + d + '/config.py'


            if not os.path.isfile(configmodule):
                continue

            mod = imp.load_source(d, configmodule)

            config = mod.Config(self)

            domain = config.get_domain()

            self.configmap[domain] = config

            domhandlerfunc = 'get_' + domain + '_config_handler'

            setattr(self, domhandlerfunc, types.MethodType(self._get_domain_config_handler, domain))


        #finalize initialization after objects are created
        #this is needed to handle inter-handler dependencies
        for domain, handler in self.configmap.iteritems():
            handler.init()



    def _get_domain_config_handler(self, domain):
        if domain not in self.configmap:
            raise configerror.ConfigError('Invalid domain')

        return self.configmap[domain]


    def mask_sensitive_data(self):
        for handler in self.configmap.values():
            try:
                handler.validate_root()
            except configerror.ConfigError:
                continue

            handler.mask_sensitive_data()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Config Manager', prog=sys.argv[0])

    parser.add_argument('--domain',
                        required=True,
                        dest='domain',
                        metavar='DOMAIN',
                        help='The configuration domain',
                        type=str,
                        action='store')

    parser.add_argument('--json',
                        required=True,
                        dest='jsonfile',
                        metavar='JSONFILE',
                        help='The json file containing the configuration',
                        type=str,
                        action='store')

    parser.add_argument('--api',
                        required=True,
                        dest='api',
                        metavar='API',
                        help='The API to call in the domain',
                        type=str,
                        action='store')

    parser.add_argument('--dump',
                        required=False,
                        dest='dump',
                        help='Dump the configuration',
                        action='store_true')

    args, unknownargs = parser.parse_known_args(sys.argv[1:])
    print("args = %r" % args)
    print("unknownargs = %r" % unknownargs)
    f = open(args.jsonfile)
    data = json.load(f)
    f.close()
    manager = ConfigManager(data)
    #domain handler func
    funcname = 'get_'+args.domain+'_config_handler'
    objfunc = getattr(manager, funcname)
    obj = objfunc()
    print('Got handler for %s' % obj.get_domain())

    domainfunc = getattr(obj, args.api)
    result = None
    if unknownargs:
        result = domainfunc(*unknownargs)
    else:
        result = domainfunc()
    print("result is %r" % result)

    if args.dump:
        import pprint
        pp = pprint.PrettyPrinter(indent=4)
        pp.pprint(data)
