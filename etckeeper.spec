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


Name:           etckeeper
Version:        1.12
Release:        0
Summary:        Store /etc under Version Control
License:        GPL-2.0+
Group:          System/Management
Source:         http://ftp.debian.org/debian/pool/main/e/etckeeper/etckeeper_%{version}.tar.gz
Source99:       etckeeper.rpmlintrc
# PATCH-FIX-UPSTREAM etckeeper-zypp.patch bnc#884154 bkbin005@rinku.zaq.ne.jp -- fix for ZYpp
Patch0:         etckeeper-zypp.patch
Url:            http://joeyh.name/code/etckeeper/
BuildRoot:      %{_tmppath}/%{name}-%{version}-build
BuildArch:      noarch
BuildRequires:  make
%define LPM rpm
# added for bzr 2014-07-10 bkbin005@rinku.zaq.ne.jp
BuildRequires:  bzr
BuildRequires:  python-devel

%if 0%{?suse_version}
# modified 2014-07-09 bkbin005@rinku.zaq.ne.jp
# Users should be able to select VCS.
Recommends:     git
Recommends:     %{name}-cron
Recommends:     %{name}-zypp-plugin
BuildRequires:  libzypp
%define HPM zypper
%else
BuildRequires:  yum
Requires:       %{name}-cron
Requires:       %{name}-yum-plugin
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
Requires:       etckeeper

%description cron
The etckeeper-cron furnishes etckeeper collaboration function
with cron.


%if 0%{?suse_version}
%package zypp-plugin
Summary:        The etckeeper collaboration function with ZYpp
Group:          System/Management
Requires:       etckeeper
Requires:       zypp-plugin-python

%description zypp-plugin
The etckeeper-zypp-plugin furnishes etckeeper collaboration function
with ZYpp.
%else
%package yum-plugin
Summary:        The etckeeper collaboration function with yum
Group:          System/Management
Requires:       etckeeper

%description yum-plugin
The etckeeper-yum-plugin furnishes etckeeper collaboration function
with YUM.
%endif

%prep
%setup -q -n "%{name}"
%patch0 -p1

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
    PYTHON_INSTALL_OPTS="--prefix=%{_prefix} --root=%{buildroot}" \
    install

# delete 2014-07-06 bkbin005@rinku.zaq.ne.jp - does not seems to work it.
# so, delete it.
## who cares about bzr...
#rm -rf "{buildroot}{_prefix}/lib"/python*

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
# Are these right?
%dir %{python_sitelib}/bzrlib
%dir %{python_sitelib}/bzrlib/plugins
%{python_sitelib}/bzrlib/plugins/%{name}/
%{python_sitelib}/bzr_%{name}-*.egg-info

%files cron
%defattr(-,root,root)
%config(noreplace) %{_sysconfdir}/cron.daily/etckeeper

%if 0%{?suse_version}
%files zypp-plugin
%defattr(-,root,root)
%dir %{_prefix}/lib/zypp
%dir %{_prefix}/lib/zypp/plugins
%dir %{_prefix}/lib/zypp/plugins/commit
%{_prefix}/lib/zypp/plugins/commit/zypper-etckeeper.py
%else
%files yum-plugin
%defattr(-,root,root)
%config(noreplace) %{_sysconfdir}/yum/pluginconf.d/etckeeper.conf
%{_prefix}/lib/yum-plugins/etckeeper.*
%endif

%changelog
