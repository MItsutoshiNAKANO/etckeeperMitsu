# vim: set sw=4 ts=4 et nu:
#
# spec file for package etckeeper
#
# Copyright (c) 2014 SUSE LINUX Products GmbH, Nuernberg, Germany.
# Copyright (c) 2014 Mitsutoshi NAKANO <bkbin005@rinku.zaq.ne.jp>
# Copyright (c) 2013 Pascal Bleser <pascal.bleser@opensuse.org>
#
# All modifications and additions to the file contributed by third parties
# remain the property of their copyright owners, unless otherwise agreed
# upon. The license for this file, and modifications and additions to the
# file, is the same license as for the pristine package itself (unless the
# license for the pristine package is not an Open Source License, in which
# case the license is the MIT License). An "Open Source License" is a
# license that conforms to the Open Source Definition (Version 1.9)
# published by the Open Source Initiative.

# Please submit bugfixes or comments via http://bugs.opensuse.org/
#


# see https://en.opensuse.org/openSUSE:Packaging_Python#Compatibility_with_older_distributions
%{!?python_sitelib: %global python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print(get_python_lib())")}
%{!?python_sitearch: %global python_sitearch %(%{__python} -c "from distutils.sysconfig import get_python_lib; print(get_python_lib(1))")}
Name:           etckeeper
Version:        1.12+git2.g52582f7
Release:        0
Summary:        Store /etc under Version Control
License:        GPL-2.0+
Group:          System/Management
Source:         %{name}_%{version}.tar.gz
Source99:       etckeeper.rpmlintrc
Url:            http://joeyh.name/code/etckeeper/
BuildRoot:      %{_tmppath}/%{name}-%{version}-build
%define LPM rpm
BuildRequires:  make
# added for bzr 2014-07-10 bkbin005@rinku.zaq.ne.jp
BuildRequires:  bzr
BuildRequires:  python-devel

%if 0%{?suse_version}
# modified 2014-07-09 bkbin005@rinku.zaq.ne.jp
# Users should be able to select VCS.
Recommends:     git
Recommends:     %{name}-cron = %{version}-%{release}
Recommends:     %{name}-zypp-plugin = %{version}-%{release}
BuildRequires:  libzypp
%define HPM zypper
%else
BuildRequires:  yum
Requires:       %{name}-cron = %{version}-%{release}
Requires:       %{name}-yum-plugin = %{version}-%{release}
%define HPM yum
%endif

%description
The etckeeper program is a tool to let /etc be stored in a git,
mercurial, bzr or darcs repository. It hooks into yum to automatically
commit changes made to /etc during package upgrades. It tracks file
metadata that version control systems do not normally support, but that
is important for /etc, such as the permissions of /etc/shadow. It is
quite modular and configurable, while also being simple to use if you
understand the basics of working with version control.


%package cron
Summary:        The etckeeper cron function
Group:          System/Management
Requires:       cron
Requires:       etckeeper = %{version}-%{release}
Provides:       etckeeper:%{_sysconfdir}/cron.daily/etckeeper

%description cron
The etckeeper-cron furnishes etckeeper collaboration function
with cron.


%if 0%{?suse_version}
%package zypp-plugin
Summary:        The etckeeper collaboration function with ZYpp
Group:          System/Management
Requires:       etckeeper = %{version}-%{release}
Requires:       zypp-plugin-python
BuildRequires:  zypp-plugin-python
Obsoletes:      etckeeper-pkgmanager-collabo < %{version}-%{release}
Provides:       etckeeper-pkgmanager-collabo = %{version}-%{release}
Provides:       etckeeper:%{_prefix}/lib/zypp/plugins/commit/zypper-etckeeper.py

%description zypp-plugin
The etckeeper-zypp-plugin furnishes etckeeper collaboration function
with ZYpp.
%else
%package yum-plugin
Summary:        The etckeeper collaboration function with yum
Group:          System/Management
Requires:       etckeeper = %{version}-%{release}
Obsoletes:      etckeeper-pkgmanager-collabo
Provides:       etckeeper-pkgmanager-collabo = %{version}-%{release}
Provides:       etckeeper:%{_sysconfdir}/yum/pluginconf.d/etckeeper.conf

%description yum-plugin
The etckeeper-yum-plugin furnishes etckeeper collaboration function
with YUM.
%endif

%prep
%setup -q -n "%{name}"

%__perl -pi -e '
s|^(\s*)(HIGHLEVEL_PACKAGE_MANAGER)=.+|$1$2=%{HPM}|;
s|^(\s*)(LOWLEVEL_PACKAGE_MANAGER)=.+|$1$2=%{LPM}|;
s|^(\s*)(VCS)=.+|$1$2=git|;
' ./etckeeper.conf

%build
make %{?_smp_mflags}

%install
make \
    DESTDIR="%{buildroot}" \
    PYTHON_INSTALL_OPTS="--prefix=%{_prefix} --install-purelib=%{python_sitearch}" \
    install
install -D debian/cron.daily "%{buildroot}/etc/cron.daily/%{name}"

%clean
%{?buildroot:%__rm -rf "%{buildroot}"}

%files
%defattr(-,root,root)
%doc GPL README.md TODO
%{_bindir}/etckeeper
%dir %{_sysconfdir}/etckeeper
%config(noreplace) %{_sysconfdir}/etckeeper/etckeeper.conf
%dir %{_sysconfdir}/etckeeper/*.d
%config %{_sysconfdir}/etckeeper/*.d/*
%doc %{_mandir}/man8/etckeeper.8*
%config %{_sysconfdir}/bash_completion.d/etckeeper
# added python_sitelib files 2014-07-10 bkbin005@rinku.zaq.ne.jp
%{python_sitearch}/bzrlib/plugins/%{name}/
%{python_sitearch}/bzr_%{name}-*.egg-info

%files cron
%defattr(-,root,root)
%config(noreplace) %{_sysconfdir}/cron.daily/etckeeper

%if 0%{?suse_version}
%files zypp-plugin
%defattr(-,root,root)
%{_prefix}/lib/zypp/plugins/commit/zypper-etckeeper.py
%else
%files yum-plugin
%defattr(-,root,root)
%config(noreplace) %{_sysconfdir}/yum/pluginconf.d/etckeeper.conf
%{_prefix}/lib/yum-plugins/etckeeper.*
%endif

%changelog
