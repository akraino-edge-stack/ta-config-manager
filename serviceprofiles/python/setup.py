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
        name='serviceprofiles',
        version='1.0',
        license='Apache-2.0',
        long_description='serviceprofiles',
        author='Baha Mesleh',
        author_email='baha.mesleh@nokia.com',
        namespace_packages=['serviceprofiles'],
        packages=find_packages(),
        include_package_data=True,
        url='gerrite1.ext.net.nokia.com:8282/service-profiles',
        description='service profiles library',
        zip_safe=False,
        )
