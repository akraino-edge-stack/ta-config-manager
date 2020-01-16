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

#!/usr/bin/env python2

PROJECT = 'cmcli'

VERSION = '0.2'

from setuptools import setup, find_packages

setup(
    name=PROJECT,
    version=VERSION,
    description='config-manager CLI',
    author='Baha Mesleh',
    author_email='baha.mesleh@nokia.com',
    platforms=['Any'],
    scripts=[],
    provides=[],
    install_requires=['hostcli'],
    namespace_packages=['cmcli'],
    packages=find_packages('src'),
    include_package_data=True,
    package_dir={'': 'src'},
    entry_points={
        'hostcli.commands': [
            'config-manager show property = cmcli.cm:ShowProperty',
            'config-manager list properties = cmcli.cm:ListProperties',
            'config-manager delete property = cmcli.cm:DeleteProperty',
            'config-manager set property = cmcli.cm:SetProperty',
            'config-manager dump-to-file property = cmcli.cm:DumpPropertyToFile'
        ],
    },
    zip_safe=False,
)
