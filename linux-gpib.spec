%bcond_without docs
%bcond_without guile
%bcond_without perl
%bcond_with php
%bcond_without python2
%bcond_without python3
%bcond_without tcl


%global svnrev 1753
%global svndate 20180529

%global _hardened_build 1

# Kind of an ugly hack to get the kernel source directory, since in a mock
# chroot, `uname -r` does not return the right version
%global kversion %((rpm -q --qf '%%{EVR}.%%{ARCH}\\n' kernel-devel | tail -1))
%global ksrcdir %{_usrsrc}/kernels/%{kversion}

%{?with_guile:%global guile_site %{_datadir}/guile/site}

%{?with_perl:%global perlname LinuxGpib}

%if %{with php}
    # The linux-gpib driver only supports PHP 5.x, but Fedora ships with 7.X
    %{error:PHP support is currently broken.}
    
    # from: https://fedoraproject.org/wiki/Packaging:PHP
    %global php_apiver \
        %((echo 0; php -i 2>/dev/null | sed -n 's/^PHP API => //p') | tail -1)
    %global php_extdir \
        %(php-config --extension-dir 2>/dev/null || echo "undefined")
    %global php_version \
        %(php-config --version 2>/dev/null || echo 0)
%endif

%if %{with tcl}
    # this is hacky, since the copr buildroot doesn't currently provide tclsh
    # adapted from <https://src.fedoraproject.org/rpms/tcl-togl/blob/master/f/tcl-togl.spec> 
    %global tcl_version_default \
        %((rpm -q --qf '%%{VERSION}\\n' tcl-devel | tail -1 | cut -c 1-3))
    %{!?tcl_version: %global tcl_version %((echo '%{tcl_version_default}'; echo 'puts $tcl_version' | tclsh 2>/dev/null) | tail -1)}
    %{!?tcl_sitearch: %global tcl_sitearch %{_libdir}/tcl%{tcl_version}}
%endif

Name:           linux-gpib
Version:        4.1.0
Release:        1.%{svndate}svn%{svnrev}%{?dist}
Summary:        Linux GPIB (IEEE-488) userspace library and programs

License:        GPLv2+
URL:            http://linux-gpib.sourceforge.net/

# The source for this package was pulled from upstream's vcs. Use the
# below commands to generate the tarball or use the SourceForge website.
# We use zip instead of tar.gz since that is what is on SourceForge
#  $ svn export -r <svnrev> https://svn.code.sf.net/p/linux-gpib/code/trunk linux-gpib-code-<svnrev>-trunk
#  $ zip -r linux-gpib-code-<svnrev>-trunk.zip linux-gpib-code-<svnrev>-trunk
Source0:        %{name}-code-%{svnrev}-trunk.zip

Source1:        %{name}-docs.xml
Source2:        60-%{name}-adapter.rules
Source3:        %{name}-config@.service
Source4:        dkms-%{name}.conf.in

# We don't need to mknod since we can let the driver and systemd take care of it
Patch0:         %{name}-nodevnodes.patch
# We package our own udev rules and firmware loader
Patch1:         %{name}-remove-usb-autotools.patch
Patch2:         %{name}-fix-tcl-manpage.patch
Patch3:         %{name}-kernel-dont-ignore-errors.patch
Patch4:         %{name}-kernel-fix-epel-build.patch

Requires:       dkms-%{name}

Requires(post):   /sbin/ldconfig
Requires(postun): /sbin/ldconfig

BuildRequires:  autoconf >= 2.50
BuildRequires:  automake
BuildRequires:  libtool

BuildRequires:  sed

BuildRequires:  flex
BuildRequires:  bison

BuildRequires:  libxslt
BuildRequires:  docbook5-style-xsl

%{?systemd_requires}
BuildRequires:  systemd

%description
The Linux GPIB package provides support for GPIB (IEEE-488) hardware.
This packages contains the userspace libraries and programs.


%package devel
Summary:        Development files for %{name}

Requires:       %{name}%{?_isa} = %{version}-%{release}

%description devel
Development files for %{name}.


%package defaults-agilent-82357a
Summary:        Default configuration for a Agilent 82357A/B or related adapter

BuildArch:      noarch
Requires:       %{name} = %{version}-%{release}
Conflicts:      %{name}-defaults-ni-gpib-usb

%description defaults-agilent-82357a
Provides a default configuration for the the following adapters:

    - Agilent/Keysight 82357A
    - Agilent/Keysight 82357B
    - Beiming Technologies F82357
    - Beiming Technologies S82357

On install, this modifies upstream's default GPIB configuration file to set up
one adapter at /dev/gpib0, so installation should Just Work. It also sets the
adapter's name (for use with ibfind()) to "keysight-usb". It preserves
upstream's other defaults, which set the primary and secondary addresses to 0,
the timeout to 3 seconds, reads to terminate on '\n', EOI to be asserted on
writes, and the adapter as the system controller.


%package defaults-ni-gpib-usb
Summary:        Default configuration for a NI-GPIB-USB or related adapter

BuildArch:      noarch
Requires:       %{name} = %{version}-%{release}
Conflicts:      %{name}-defaults-agilent-82357a

%description defaults-ni-gpib-usb
Provides a default configuration for the the following adapters:

    - Keithley KUSB-488
    - Keithley KUSB-488A
    - Measurement Computing (Computer Boards) USB-488
    - National Instruments GPIB-USB-B
    - National Instruments GPIB-USB-HS
    - National Instruments GPIB-USB-HS+

On install, this modifies upstream's default GPIB configuration file to set up
one adapter at /dev/gpib0, so installation should Just Work. It also sets the
adapter's name (for use with ibfind()) to "ni-usb". It preserves
upstream's other defaults, which set the primary and secondary addresses to 0,
the timeout to 3 seconds, reads to terminate on '\n', EOI to be asserted on
writes, and the adapter as the system controller.


%package -n dkms-%{name}
Summary:        Linux GPIB (IEEE-488) driver

# since the package just distributes the source for
# compilation by dkms, this package can be noarch
BuildArch:      noarch
# TODO: do we need to limit the archs this will run on?
#ExclusiveArch:  ????

Requires:           dkms
Requires(post):     /sbin/ldconfig
Requires(postun):   /sbin/ldconfig

BuildRequires:      kmod
BuildRequires:      kernel-headers
BuildRequires:      kernel-devel
BuildRequires:      elfutils-libelf-devel

%description -n dkms-%{name}
The Linux GPIB package provides support for GPIB (IEEE-488) hardware.

This packages contains the kernel drivers for adapters compatible with:
    - Agilent/Keysight 82350B
    - Agilent/Keysight 82357A/B
    - CB7210
    - Capital Equipment Corporation GPIB cards
    - FMH GPIB HDL core
    - HP 82335
    - HP 82341
    - INES PCI cards
    - LPVO USB GPIB
    - NEC7210
    - NI GPIB-USB-B/HS/HS+
    - TMS9914
    - TNT4882


%if %{with guile}
%package -n guile18-%{name}
Summary:        Guile %{name} module

Requires:       compat-guile18%{?_isa}
Requires:       %{name}%{?_isa} = %{version}-%{release}
BuildRequires:  compat-guile18-devel

%description -n guile18-%{name}
Guile bindings for %{name}.
%endif


%if %{with php}
%package -n php-%{name}
Summary:        PHP %{name} module

Requires:       %{name}%{?_isa} = %{version}-%{release}
Requires:       php(zend-abi) = %{php_zend_api}
Requires:       php(api) = %{php_core_api}
BuildRequires:  php-devel
BuildRequires:  php-zendframework

%description -n php-%{name}
PHP bindings for %{name}.
%endif


%if %{with perl}
%package -n perl-%{perlname}
Summary:        Perl %{name} module

Requires:       perl
Requires:       %{name}%{?_isa} = %{version}-%{release}
BuildRequires:  perl-devel
BuildRequires:  perl(ExtUtils::MakeMaker)
BuildRequires:  perl(Test)

%description -n perl-%{perlname}
Perl bindings for %{name}.
%endif


%if %{with python2}
%package -n python2-%{name}
Summary:        Python 2 %{name} module

%{?python_provide:%python_provide python2-%{name}}
Requires:      %{name}%{?_isa} = %{version}-%{release}
BuildRequires:  python2-devel

%description -n python2-%{name}
Python 2 bindings for %{name}.
%endif


%if %{with python3}
%package -n python%{python3_pkgversion}-%{name}
Summary:        Python 3 %{name} module

%{?python_provide:%python_provide python%{python3_pkgversion}-%{name}}
Requires:       %{name}%{?_isa} = %{version}-%{release}
BuildRequires:  python%{python3_pkgversion}-devel

%description -n python%{python3_pkgversion}-%{name}
Python 3 bindings for %{name}.
%endif


%if %{with tcl}
%package -n tcl-%{name}
Summary:        TCL %{name} module

Requires:       tcl(abi) = %{tcl_version}
Requires:       %{name}%{?_isa} = %{version}-%{release}
BuildRequires:  tcl-devel

%description -n tcl-%{name}
TCL bindings for %{name}.
%endif


%if %{with docs}
%package doc
Summary:        Documentation for %{name} library

BuildArch:      noarch
Requires:       %{name} = %{version}-%{release}
BuildRequires:  dblatex

%description doc
HTML and PDF documentation for %{name}.
%endif


%prep
%setup -q -n %{name}-code-%{svnrev}-trunk

%patch0 -p1
%patch1 -p1
%patch2 -p1
%patch3 -p1
%{?el7:%patch4 -p1}

pushd %{name}-kernel
sed -e 's/__VERSION_STRING/%{version}/g' %{SOURCE4} > dkms.conf
popd

%build
pushd %{name}-kernel
autoreconf -vif

# With dkms, we don't actually distribute the binary kernel modules, but
# this invokation of ./configure just generates a makefile so we can run
# `make dist`, which will give us a clean package of the kernel module 
# source for dkms to compile. We test that it actually compiles in
# the %%check section.
%configure --with-linux-srcdir=%{ksrcdir}
%{__make} dist
popd

pushd %{name}-user
autoreconf -vif

# we make the docs, and the Perl and Python bindings in the spec, 
# not the library's Makefile
%configure \
    %{!?with_guile:--disable-guile18-binding} \
    %{!?with_php:--disable-php-binding} \
    %{!?with_tcl:--disable-tcl-binding} \
    --disable-documentation \
    --disable-python-binding \
    --disable-perl-binding \
    --disable-static

%make_build

pushd language/perl
%if %{with perl}
    %{__perl} Makefile.PL INSTALLDIRS=vendor NO_PACKLIST=1 OPTIMIZE="%{optflags}"
    %make_build
%endif
popd

pushd language/python
%{?with_python2:%py2_build}
%{?with_python3:%py3_build}
popd
popd # %%{name}-user


%install
# build directory tree
install -d %{buildroot}%{_docdir}/%{name}
install -d %{buildroot}%{_mandir}/{man1,man3,man5,man8,mann}

%{?with_guile:install -d %{buildroot}%{guile_site}}
%{?with_tcl:install -d %{buildroot}%{tcl_sitearch}/%{name}}

# dkms package
pushd %{name}-kernel
install -d %{buildroot}%{_usrsrc}/%{name}-%{version}-%{release}
%{__tar} -xf %{name}-kernel-%{version}.tar.gz \
         -C %{buildroot}%{_usrsrc}/%{name}-%{version}-%{release} \
         --strip-components=1 --preserve-permissions --preserve-order
install -p -m 0644 dkms.conf %{buildroot}%{_usrsrc}/%{name}-%{version}-%{release}
popd

# userspace
pushd %{name}-user
%make_install

pushd language
pushd guile
%{?with_guile:install -p -m 0644 gpib.scm %{buildroot}%{guile_site}}
popd

pushd perl
%{?with_perl:%{__make} pure_install DESTDIR=%{buildroot}}
popd

pushd python
%{?with_python2:%py2_install}
%{?with_python3:%py3_install}
popd

pushd tcl
%if %{with tcl}
    mv %{buildroot}%{_libdir}/*_tcl* %{buildroot}%{tcl_sitearch}/%{name}
    install -p -m 0644 gpib.n %{buildroot}%{_mandir}/mann
%endif
popd
popd # language

pushd doc
echo '<phrase xmlns="http://docbook.org/ns/docbook" version="5.0">%{version}</phrase>' > %{name}-version.xml
cp -fp %{SOURCE1} %{name}.xml

xsltproc --param man.authors.section.enabled 0 \
         --param man.output.in.separate.dir 1 \
         --xinclude \
         %{_datadir}/sgml/docbook/xsl-ns-stylesheets/manpages/docbook.xsl \
         %{name}.xml

for mandir in man1 man3 man5 man8 ; do
    install -p -m 0644 man/$mandir/* %{buildroot}%{_mandir}/$mandir
done

%if %{with docs}
    dblatex %{name}.xml -P table.in.float=none -o %{name}.pdf
    install -p -m 0644 %{name}.pdf %{buildroot}%{_docdir}/%{name}

    install -p -m 0644 %{name}.xml %{buildroot}%{_docdir}/%{name}
    install -p -m 0644 %{name}-version.xml %{buildroot}%{_docdir}/%{name}
    install -p -m 0644 obsolete-linux-gpib.txt %{buildroot}%{_docdir}/%{name}

    xsltproc --param generate.revhistory.link 1 \
             --param generate.section.toc.level 2 \
             --param make.clean.html 1 \
             --param table.borders.with.css 1 \
             --param use.id.as.filename 1 \
             --stringparam base.dir "html" \
             --stringparam chunker.output.omit-xml-declaration "yes" \
             --stringparam html.ext ".html" \
             --xinclude \
             %{_datadir}/sgml/docbook/xsl-ns-stylesheets/xhtml5/chunk.xsl \
             %{name}.xml
    
    install -d %{buildroot}%{_docdir}/%{name}/html
    install -p -m 0644 html/* %{buildroot}%{_docdir}/%{name}/html
%endif
popd # doc

# udev rules
install -d %{buildroot}%{_udevrulesdir}
install -p -m 0644 %{SOURCE2} %{buildroot}%{_udevrulesdir}

# systemd config unit
install -d %{buildroot}%{_unitdir}
install -p -m 0644 %{SOURCE3} %{buildroot}%{_unitdir}
popd # %%{name}-user

# Cleanup
# remove libtool stuff
find %{buildroot} -name '*.la' -delete

# ... and automake caches `make dist` didn't get rid of
find %{buildroot} -name '.cache.mk' -delete

# ... and static libraries for language bindings
%{?with_guile:rm -f %{buildroot}%{_libdir}/*-guile.a}
%{?with_tcl:rm -f %{buildroot}%{tcl_sitearch}/%{name}/*_tcl.a}

# ... and .packlist for EPEL7 package
%{?with_perl:find %{buildroot} -type f -name '*.packlist' -delete}


%check
pushd %{name}-user/language/perl
%{?with_perl:%{__make} test LD_LIBRARY_PATH=%{buildroot}%{_libdir}}
popd

# Sanity check to make sure the kernel modules compile
pushd %{name}-kernel
%configure --with-linux-srcdir=%{ksrcdir}
%make_build
popd


# Post-install stuff

# Default configurations
%post defaults-agilent-82357a
# on initial install only
if [ $1 -eq 1 ] ; then
    sed -i -E -e 's/board_type = "ni_(pci|usb_b)"/board_type = "agilent_82357a"/' \
              -e 's/name = "(violet|ni-usb)"/name = "keysight-usb"/' \
              %{_sysconfdir}/gpib.conf || :
fi

%post defaults-ni-gpib-usb
# on initial install only
if [ $1 -eq 1 ] ; then
    sed -i -E -e 's/board_type = "(ni_pci|agilent_82357a)"/board_type = "ni_usb_b"/' \
              -e 's/name = "(violet|keysight-usb)"/name = "ni-usb"/' \
              %{_sysconfdir}/gpib.conf || :
fi

# systemd stuff
%post
%systemd_post %{name}-config@.service
%{?ldconfig}

%preun
%systemd_preun %{name}-config@.service

%postun 
%systemd_postun %{name}-config@.service
%{?ldconfig}

# and ldconfig
%ldconfig_scriptlets devel

%{?with_guile:%ldconfig_scriptlets -n guile18-%{name}}

%{?with_tcl:%ldconfig_scriptlets -n tcl-%{name}}

# dkms
# Adapted from <https://github.com/negativo17/dkms-nvidia/blob/master/dkms-nvidia.spec>
%post -n dkms-%{name}
dkms add -m %{name} -v %{version}-%{release} -q --rpm_safe_upgrade || :
# Rebuild and make available for the currently running kernel
dkms build -m %{name} -v %{version}-%{release} -q || :
dkms install -m %{name} -v %{version}-%{release} -q --force || :

%{?ldconfig}
udevadm control --reload > /dev/null 2>&1 || :

%preun -n dkms-%{name}
# Remove all versions from DKMS registry
dkms remove -m %{name} -v %{version}-%{release} -q --all --rpm_safe_upgrade || :
%{?ldconfig}
udevadm control --reload > /dev/null 2>&1 || :


%files
%defattr(644,root,root,755)

%license %{name}-user/COPYING
%doc %{name}-user/README

%attr(755,root,root) %{_bindir}/ibterm
%attr(755,root,root) %{_bindir}/ibtest
%attr(755,root,root) %{_sbindir}/gpib_config

%{_mandir}/man1/*
%{_mandir}/man5/*
%{_mandir}/man8/*

%{_libdir}/libgpib.so.*

%config(noreplace) %{_sysconfdir}/gpib.conf

%{_unitdir}/*.service
%{_udevrulesdir}/*.rules

%files defaults-agilent-82357a
%config(noreplace) %{_sysconfdir}/gpib.conf

%files defaults-ni-gpib-usb
%config(noreplace) %{_sysconfdir}/gpib.conf

%files -n dkms-%{name}

%doc %{name}-kernel/README %{name}-kernel/AUTHORS %{name}-kernel/INSTALL
%license %{name}-kernel/COPYING

%dir %{_usrsrc}/%{name}-%{version}-%{release}
%{_usrsrc}/%{name}-%{version}-%{release}/*
%exclude %{_usrsrc}/%{name}-%{version}-%{release}/NEWS


%files devel
%defattr(644,root,root,755)

%doc %{name}-user/README
%license %{name}-user/COPYING

%dir %{_includedir}/gpib

%{_includedir}/gpib/gpib_user.h
%{_includedir}/gpib/ib.h
%{_libdir}/pkgconfig/libgpib.pc
%{_libdir}/libgpib.so

%{_mandir}/man3/*.3*

%if %{with perl}
%exclude %{_mandir}/man3/*.3pm*
%endif


%if %{with guile}
%files -n guile18-%{name}
%defattr(644,root,root,755)

%doc %{name}-user/language/guile/README
%license %{name}-user/COPYING

%{_libdir}/*-guile*.so
%{guile_site}/*.scm
%endif


%if %{with python3}
%files -n python%{python3_pkgversion}-%{name}
%defattr(644,root,root,755)

%doc %{name}-user/language/python/README
%license %{name}-user/COPYING

%{python3_sitearch}/*
%endif


%if %{with python2}
%files -n python2-%{name}
%defattr(644,root,root,755)

%doc %{name}-user/language/python/README
%license %{name}-user/COPYING

%{python2_sitearch}/*
%endif


%if %{with perl}
%files -n perl-%{perlname}
%defattr(644,root,root,755)

%doc %{name}-user/language/perl/README
%license %{name}-user/COPYING

%dir %{perl_vendorarch}/auto/%{perlname}

%{perl_vendorarch}/%{perlname}.pm
%{perl_vendorarch}/auto/%{perlname}/%{perlname}.*
%{perl_vendorarch}/auto/%{perlname}/autosplit.ix

%{_mandir}/man3/*.3pm*
%endif


%if %{with tcl}
%files -n tcl-%{name}
%defattr(644,root,root,755)

%doc %{name}-user/language/tcl/README
%license %{name}-user/COPYING

%{tcl_sitearch}/%{name}

%{_mandir}/mann/gpib.n*
%endif


%if %{with docs}
%files doc
%defattr(644,root,root,755)

%license %{name}-user/doc/fdl.xml

%{_docdir}/%{name}
%endif


%changelog
* Sat Jun 16 2018 Colin Samples <colin-dot-samples-at-gmail-dot-com> - 4.1.0-1.20180529svn1753
- Initial release
