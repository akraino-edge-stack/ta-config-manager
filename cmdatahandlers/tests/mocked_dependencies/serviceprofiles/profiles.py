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

import os
import re
import inspect

class Profile(object):
    def __init__(self):
        self.name = None
        self.description = None
        self.inherits = []
        self.included_profiles = []
    def __str__(self):
        return 'name:{}\ndescription:{}\ninherits:{}\nincluded_profiles:{}\n'.format(self.name, self.description, self.inherits, self.included_profiles)

class Profiles(object):
    def __init__(self, location=os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))):
        self.location = location
        self.profiles = {}
        try:
            self._load_profiles()
        except:
            pass

    def _load_profiles(self):
        files = self._get_profiles_files()
        for f in files:
            self._profile_from_file(f)

        #update the included profiles
        for name, profile in self.profiles.iteritems():
            included_profiles = []
            self._update_included_profiles(profile, included_profiles)
            profile.included_profiles = included_profiles


    def _update_included_profiles(self, profile, included_profiles):
        included_profiles.append(profile.name)
        for b in profile.inherits:
            self._update_included_profiles(self.profiles[b], included_profiles)
            
    def _get_profiles_files(self):
        files = os.listdir(self.location)
        pattern = re.compile('.*[.]profile$')
        result = []
        for f in files:
            fullpath = self.location + '/' + f
            if os.path.isfile(fullpath) and pattern.match(f):
                result.append(fullpath)
        return result



    def _profile_from_file(self, filename):
        profile = Profile()
        with open(filename) as f:
            lines=f.read().splitlines()
            for l in lines:
                data = l.split(':')
                if len(data) != 2:
                    raise Exception('Invalid line %s in file %s' % (l, filename))
                elif data[0] == 'name':
                    profile.name = data[1]
                elif data[0] == 'description':
                    profile.description = data[1]
                elif data[0] == 'inherits':
                    profile.inherits = data[1].split(',')
                else:
                    raise Exception('Invalid line %s in file %s' % (l, filename))
        self.profiles[profile.name] = profile

    def get_included_profiles(self, name):
        return self.profiles[name].included_profiles

    def get_profiles(self):
        return self.profiles

    def get_children_profiles(self, name):
        ret = []
        for pfname, profile in self.profiles.iteritems():
            if name in profile.inherits:
                ret.append(pfname)
        return ret


if __name__ == '__main__':
    import sys
    import traceback
    import argparse

    parser = argparse.ArgumentParser(description='Test service profiles',
            prog=sys.argv[0])


    parser.add_argument('--get-included-profiles',
            dest='get_included_profiles',
            help='Get the profiles included in some profile name',
            action='store_true')

    parser.add_argument('--get-all-profiles',
            help='Get the profiles list',
            dest='get_all_profiles',
            action='store_true')

    parser.add_argument('--get-children-profiles',
            dest='get_children_profiles',
            help='Get the children of a profile',
            action='store_true')

    parser.add_argument('--name',
            metavar='NAME',
            dest='name',
            help='The name of the profile',
            type=str,
            action='store')
    try:
        args = parser.parse_args(sys.argv[1:])
        profiles = Profiles()
        if args.get_included_profiles or args.get_children_profiles:
            if not args.name:
                raise Exception('Missing profile name')
           
            if args.get_included_profiles:
                included_profiles = profiles.get_included_profiles(args.name)
                print('Included profiles')
                for p in included_profiles:
                    print(p)
            if args.get_children_profiles:
                children_profiles = profiles.get_children_profiles(args.name)
                print('Children profiles')
                for p in children_profiles:
                    print(p)
        elif args.get_all_profiles:
            all = profiles.get_profiles()
            for name, p in all.iteritems():
                print(p)
    except Exception as exp:
        print('Failed with error %s' % exp)
        traceback.print_exc()
        sys.exit(1)
