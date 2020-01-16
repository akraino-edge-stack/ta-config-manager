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

from setuptools import setup, find_packages
setup(
    name='cmframework',
    version='1.0',
    license='Apache-2.0',
    long_description='README.txt',
    author='Baha Mesleh',
    author_email='baha.mesleh@nokia.com',
    namespace_packages=['cmframework'],
    packages=find_packages(),
    include_package_data=True,
    package_data={'cmframework.tst': ['*.py', '*.sh']},
    url='https://gitlab.fp.nsn-rdnet.net/mesleh/cmframework',
    description='Configuration Management Framework',
    entry_points={
        'console_scripts': [
            'cmserver = cmframework.server.cmserver:main',
            'cmcli = cmframework.cli.cmcli:main',
            'cmagent = cmframework.agent.cmagent:main'
        ],
    },
    zip_safe=False,
    python_requires='~=2.7,<3.0',
)
