#!/usr/bin/env python
# -*- coding: utf-8 -*-

import shutil, os, re, glob
from conans import ConanFile, tools, AutoToolsBuildEnvironment


class LibdrmConan(ConanFile):
    name            = 'libdrm'
    version         = '2.4.75'
    license         = 'MIT'
    url             = 'https://github.com/kheaactua/conan-libdrm.git'
    description     = 'https://01.org/linuxgraphics'
    md5_hash        = '743c16109d91a2539dfc9cc56130d695'
    requires        = 'helpers/[>=0.3]@ntc/stable'

    settings = {
        'compiler': None,
        'os_build':   ['Linux'],
        'arch_build': ['x86_64'],
        'build_type': None,
    }

    def system_requirements(self):
        pack_names = None
        if 'ubuntu' == tools.os_info.linux_distro:
            pack_names = ['libpciaccess-dev' ]

        if pack_names:
            installer = tools.SystemPackageTool()
            try:
                # installer.update() # Update the package database
                installer.install(' '.join(pack_names)) # Install the package
            except ConanException:
                self.output.warn('Could not run system requirements installer.  Required packages might be missing.')

    def build_requirements(self):
        pack_names = None
        if 'ubuntu' == tools.os_info.linux_distro:
            pack_names = ['autoconf', 'autopoint', 'automake', 'autotools-dev', 'libtool', 'autopoint']

        if pack_names:
            installer = tools.SystemPackageTool()
            try:
                # installer.update() # Update the package database
                installer.install(' '.join(pack_names)) # Install the package
            except ConanException:
                self.output.warn('Could not run build requirements installer.')

    def source(self):
        # Found this at https://01.org/linuxgraphics/downloads/2017q1-intel-graphics-stack-recipe
        archive = 'libdrm-%s'%self.version
        archive_file = '%s.tar.gz'%archive
        url = 'http://dri.freedesktop.org/libdrm/%s'%archive_file

        from source_cache import copyFromCache
        if not copyFromCache(archive_file):
            tools.download(url=url, filename=archive_file)
            tools.check_md5(archive_file, self.md5_hash)
        tools.unzip(archive_file)
        shutil.move(archive, self.name)
        os.remove(archive_file)

    def build(self):
        args = []
        args.append('--prefix=%s'%self.package_folder)

        autotools = AutoToolsBuildEnvironment(self)

        with tools.chdir(self.name):
            autotools.configure(args=args)
            autotools.make()
            autotools.install()

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)

        # Populate the pkg-config environment variables
        with tools.pythonpath(self):
            from platform_helpers import adjustPath, appendPkgConfigPath

            pkg_config_path = os.path.join(self.package_folder, 'lib', 'pkgconfig')
            appendPkgConfigPath(adjustPath(pkg_config_path), self.env_info)

            pc_files = glob.glob(adjustPath(os.path.join(pkg_config_path, '*.pc')))
            for f in pc_files:
                p_name = re.sub(r'\.pc$', '', os.path.basename(f))
                p_name = re.sub(r'\W', '_', p_name.upper())
                setattr(self.env_info, 'PKG_CONFIG_%s_PREFIX'%p_name, adjustPath(self.package_folder))

            appendPkgConfigPath(adjustPath(pkg_config_path), self.env_info)

# vim: ts=4 sw=4 expandtab ffs=unix ft=python foldmethod=marker :
