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

Name:       config-manager
Version:    %{_version}
Release:    1%{?dist}
Summary:    Contains code for the config manager
License:    %{_platform_licence}
Source0:    %{name}-%{version}.tar.gz
Vendor:     %{_platform_vendor}
BuildArch:  noarch

BuildRequires: python2
BuildRequires: python2-setuptools
Requires:      python2, redis, python2-eventlet, python2-routes, python2-redis

%description
This RPM contains source code for the config manager.

%prep
%autosetup

%install
mkdir -p %{buildroot}/opt/cmframework/activators
mkdir -p %{buildroot}/opt/cmframework/validators
mkdir -p %{buildroot}/opt/cmframework/userconfighandlers
mkdir -p %{buildroot}/opt/cmframework/inventoryhandlers
mkdir -p %{buildroot}/etc/cmframework/masks.d

mkdir -p %{buildroot}/opt/cmframework/scripts
cp cmframework/scripts/*.sh %{buildroot}/opt/cmframework/scripts
cp cmframework/scripts/cmserver %{buildroot}/opt/cmframework/scripts
cp cmframework/scripts/cmagent %{buildroot}/opt/cmframework/scripts
cp cmframework/scripts/redis.conf %{buildroot}/opt/cmframework/scripts
cp cmframework/config/masks.d/default.cfg %{buildroot}/etc/cmframework/masks.d/

mkdir -p %{buildroot}/usr/lib/systemd/system
cp cmframework/systemd/config-manager.service  %{buildroot}/usr/lib/systemd/system
cp cmframework/systemd/cmagent.service  %{buildroot}/usr/lib/systemd/system

mkdir -p %{buildroot}/%{_python_site_packages_path}/cmframework/
set -e
cd cmframework/src && python2 setup.py install --root %{buildroot} --no-compile --install-purelib %{_python_site_packages_path} --install-scripts %{_platform_bin_path} && cd -

cd cmdatahandlers && python setup.py install --root %{buildroot} --no-compile --install-purelib %{_python_site_packages_path} --install-scripts %{_platform_bin_path} && cd -

mkdir -p %{buildroot}/etc/service-profiles/
cp serviceprofiles/profiles/*.profile %{buildroot}/etc/service-profiles/

cd serviceprofiles/python && python setup.py install --root %{buildroot} --no-compile --install-purelib %{_python_site_packages_path} && cd -

cd hostcli && python setup.py install --root %{buildroot} --no-compile --install-purelib %{_python_site_packages_path} && cd -

%files
%defattr(0755,root,root,0755)
/opt/cmframework
/usr/lib/systemd/system/config-manager.service
/usr/lib/systemd/system/cmagent.service
%{_platform_bin_path}/cmserver
%{_platform_bin_path}/cmcli
%{_platform_bin_path}/cmagent
%dir /etc/cmframework/masks.d
/etc/cmframework/masks.d/default.cfg
%{_python_site_packages_path}/cmframework*
%{_python_site_packages_path}/cmdatahandlers*
%{_python_site_packages_path}/serviceprofiles*
%{_python_site_packages_path}/cmcli*
/etc/service-profiles/*

%pre

%post
mkdir -p /opt/openstack-ansible/inventory/
ln -sf /opt/cmframework/scripts/inventory.sh /opt/openstack-ansible/inventory/
chmod -x /usr/lib/systemd/system/config-manager.service
chmod -x /usr/lib/systemd/system/cmagent.service

%preun

%postun

%clean
rm -rf %{buildroot}
