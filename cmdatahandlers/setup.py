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
        name='cmdatahandlers',
        version='1.0',
        license='Apache-2.0',
        long_description='README',
        author='Baha Mesleh',
        author_email='baha.mesleh@nokia.com',
        namespace_packages=['cmdatahandlers'],
        packages=find_packages('src'),
        include_package_data=True,
        package_dir={'': 'src'},
        description='Configuration Data Handlers',
        zip_safe=False,
)
