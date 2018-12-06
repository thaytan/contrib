#!/usr/bin/env python
# -*- coding: utf-8 -*-

from conans import ConanFile, tools, AutoToolsBuildEnvironment
import os


class YASMInstallerConan(ConanFile):
    name = "yasm_installer"
    version = "1.3.0"
    url = "https://github.com/bincrafters/conan-yasm_installer"
    description = "Yasm is a complete rewrite of the NASM assembler under the “new” BSD License"
    license = "https://github.com/yasm/yasm/blob/master/BSD.txt"
    exports_sources = ["LICENSE"]
    settings = "os_build", "arch_build", "compiler"
    _source_subfolder = "sources"

    def source(self):
        source_url = "http://www.tortall.net/projects/yasm/releases/yasm-%s.tar.gz" % self.version
        tools.get(source_url)
        extracted_dir = 'yasm-%s' % self.version
        os.rename(extracted_dir, self._source_subfolder)
        tools.download('https://raw.githubusercontent.com/yasm/yasm/master/YASM-VERSION-GEN.bat',
                       os.path.join('sources', 'YASM-VERSION-GEN.bat'))

    def build(self):
        if self.settings.os_build == 'Windows':
            self._build_vs()
        else:
            self._build_configure()

    def _build_vs(self):
        with tools.chdir(os.path.join(self._source_subfolder, 'Mkfiles', 'vc10')):
            with tools.vcvars(self.settings, arch=str(self.settings.arch_build), force=True):
                command = tools.build_sln_command(self.settings, 'yasm.sln', arch=self.settings.arch_build,
                                                  build_type='Release', targets=['yasm'], upgrade_project=True)
                if self.settings.arch_build == 'x86':
                    command = command.replace('/p:Platform="x86"', '/p:Platform="Win32"')
                self.run(command)

    def _build_configure(self):
        with tools.chdir(self._source_subfolder):
            cc = os.environ.get('CC', 'gcc')
            cxx = os.environ.get('CXX', 'g++')
            # TODO : PR to AutoToolsBuildEnvironment
            if self.settings.arch_build == 'x86':
                cc = cc + ' -m32'
                cxx = cxx + ' -m32'
            elif self.settings.arch_build == 'x86_64':
                cc = cc + ' -m64'
                cxx = cxx + ' -m64'
            with tools.environment_append({'CC': cc, 'CXX': cxx}):
                env_build = AutoToolsBuildEnvironment(self)
                env_build.configure()
                env_build.make()
                env_build.install()

    def package(self):
        with tools.chdir(self._source_subfolder):
            self.copy(pattern="BSD.txt", dst="licenses")
        if self.settings.os_build == 'Windows':
            self.copy(pattern='*.exe', src=self._source_subfolder, dst='bin', keep_path=False)

    def package_info(self):
        self.env_info.PATH.append(os.path.join(self.package_folder, 'bin'))

    def package_id(self):
        self.info.settings.compiler = 'Any'
