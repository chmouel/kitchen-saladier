%define _version NOVERSION

Name:           kitchen-saladier
Version:        %{_version}
Release:        1%{?dist}
Summary:        Kitchen Saladier

License:        ASL 2.0
Source0:        %{name}-%{version}.tar.gz
Source1:        kitchen-saladier.logrotate
Source2:        kitchen-saladier.service
Source3:        kitchen-saladier.sysctl

BuildArch:      noarch

Requires:       python-kitchen-saladier = %{version}-%{release}
BuildRequires:  python2-devel
BuildRequires:  python-sphinx >= 1.0
BuildRequires:  python-oslo-sphinx
BuildRequires:  systemd-units
BuildRequires:  python-pbr
BuildRequires:  python-d2to1
BuildRequires:  python-mock
BuildRequires:  python-oslo-config >= 1:1.2.0

Requires(post):   systemd-units
Requires(preun):  systemd-units
Requires(postun): systemd-units
Requires(pre):    shadow-utils

%description
http://en.wiktionary.org/wiki/saladier - *A salad bowl, a mixing bowl*

Sitting between the product server and the different CIs the saladier
is central to the **kitchen-island** project.

The Saladier is the service that collect results of deployment for the
different products that has been certified on the different CI and
gives the authorization for the final deployment according to
different set of rules.

This is the servers and configuration files packages.

%package -n       python-kitchen-saladier
Summary:          Saladier Python libraries
Group:            Applications/System


Requires:       python-keystonemiddleware
Requires:       python-pecan
Requires:       python-pbr
Requires:       python-paste-deploy
Requires:       python-sqlalchemy
Requires:       python-oslo-config >= 1:1.2.0
Requires:       python-oslo-db
Requires:       python-oslo-serialization
Requires:       python-netaddr
Requires:       python-six >= 1.4.1
Requires:       python-babel
Requires:       python-oauthlib
# Until pymysql rpm is available
Requires:       MySQL-python

%description -n   python-kitchen-saladier
http://en.wiktionary.org/wiki/saladier - *A salad bowl, a mixing bowl*

Sitting between the product server and the different CIs the saladier
is central to the **kitchen-island** project.

The Saladier is the service that collect results of deployment for the
different products that has been certified on the different CI and
gives the authorization for the final deployment according to
different set of rules.

This is the python libs and dirs.

%prep
%setup -q -n kitchen-saladier-%{version}

find . \( -name .gitignore -o -name .placeholder \) -delete
find saladier -name \*.py -exec sed -i '/\/usr\/bin\/env python/d' {} \;
# Remove bundled egg-info

%build
%{__python} setup.py build

oslo-config-generator --output-file etc/saladier/saladier.conf \
               --namespace saladier \
               --namespace keystonemiddleware.auth_token \
               --namespace oslo.db

sed -i 's,^#connection = ,connection=mysql://saladier:password@localhost/saladier,' etc/saladier/saladier.conf

%install
%{__python} setup.py install --skip-build --root %{buildroot}

# Delete tests
rm -fr %{buildroot}%{python_sitelib}/saladier/tests

install -d -m 755 %{buildroot}%{_sysconfdir}/saladier
install -p -D -m 640 etc/saladier/saladier.conf %{buildroot}%{_sysconfdir}/saladier/
install -p -D -m 644 etc/saladier/api_paste.ini %{buildroot}%{_sysconfdir}/saladier/

install -p -D -m 644 %{SOURCE1} %{buildroot}%{_sysconfdir}/logrotate.d/kitchen-saladier
install -p -D -m 644 %{SOURCE2} %{buildroot}%{_unitdir}/kitchen-saladier.service
install -d -m 755 %{buildroot}%{_sysctldir}
install -p -D -m 644 %{SOURCE3} %{buildroot}%{_sysctldir}/kitchen-saladier.conf

install -d -m 755 %{buildroot}%{_sharedstatedir}/saladier
install -d -m 755 %{buildroot}%{_localstatedir}/log/saladier

%pre
getent group saladier >/dev/null || groupadd -r saladier
getent passwd saladier >/dev/null || \
useradd -r -g saladier -d %{_sharedstatedir}/saladier -s /sbin/nologin \
-c "Kitchen Saladier Daemons" saladier
exit 0

%post
if [ $1 -eq 1 ] ; then
    # Initial installation
    /bin/systemctl daemon-reload >/dev/null 2>&1 || :
fi

%preun
if [ $1 -eq 0 ] ; then
    # Package removal, not upgrade
    /bin/systemctl --no-reload disable kitchen-saladier.service > /dev/null 2>&1 || :
    /bin/systemctl stop kitchen-saladier.service > /dev/null 2>&1 || :
fi

%postun
/bin/systemctl daemon-reload >/dev/null 2>&1 || :
if [ $1 -ge 1 ] ; then
    # Package upgrade, not uninstall
    /bin/systemctl try-restart kitchen-saladier.service >/dev/null 2>&1 || :
fi

%files
%doc LICENSE
%doc README.rst
%{_bindir}/saladier-api
%{_bindir}/saladier-dbsync
%dir %attr(0750, root, saladier) %{_sysconfdir}/saladier
%config(noreplace) %attr(0644, root, saladier) %{_sysconfdir}/saladier/api_paste.ini
%config(noreplace) %attr(0640, root, saladier) %{_sysconfdir}/saladier/saladier.conf
%dir %attr(-, saladier, saladier) %{_sharedstatedir}/saladier
%dir %attr(0750, saladier, saladier) %{_localstatedir}/log/saladier
%{_unitdir}/kitchen-saladier.service
%config(noreplace) %{_sysconfdir}/logrotate.d/kitchen-saladier
%{_sysctldir}/kitchen-saladier.conf

%files -n python-kitchen-saladier
%defattr(-,root,root,-)
%doc LICENSE
%{python_sitelib}/saladier
%{python_sitelib}/kitchen_saladier-%{version}-*.egg-info

%changelog
* Tue Dec 30 2014 Chmouel Boudjnah <chmouel@enovance.com> - 4b400ce-1
- First version based on other standard OpenStack packages.
