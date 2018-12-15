#!/usr/bin/env python
# -*- coding: utf-8 -*-

from conans import ConanFile, tools, AutoToolsBuildEnvironment, MSBuild
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
            # fix invalid solution configurations
            tools.replace_in_file('yasm.sln', 'Debug|x64.ActiveCfg = Debug|Win32',
                                  'Debug|x64.ActiveCfg = Debug|x64')
            tools.replace_in_file('yasm.sln', 'Debug|x64.Build.0 = Debug|Win32',
                                  'Debug|x64.Build.0 = Debug|x64')
            tools.replace_in_file('yasm.sln', 'Release|x64.ActiveCfg = Release|Win32',
                                  'Release|x64.ActiveCfg = Release|x64')
            tools.replace_in_file('yasm.sln', 'Release|x64.Build.0 = Release|Win32',
                                  'Release|x64.Build.0 = Release|x64')

            with tools.vcvars(self.settings, arch=str(self.settings.arch_build), force=True):
                msbuild = MSBuild(self)
                msbuild.build(project_file="yasm.sln", arch=self.settings.arch_build, build_type="Release",
                              targets=["yasm"], platforms={"x86": "Win32"})

    def _build_configure(self):
        with tools.chdir(self._source_subfolder):
            cc = os.environ.get('CC', 'gcc')
            cxx = os.environ.get('CXX', 'g++')
            if self.settings.arch_build == 'x86':
                cc += ' -m32'
                cxx += ' -m32'
            elif self.settings.arch_build == 'x86_64':
                cc += ' -m64'
                cxx += ' -m64'
            env_build = AutoToolsBuildEnvironment(self)
            env_build_vars = env_build.vars
            env_build_vars.update({'CC': cc, 'CXX': cxx})
            env_build.configure(vars=env_build_vars)
            env_build.make(vars=env_build_vars)
            env_build.install(vars=env_build_vars)

    def package(self):
        with tools.chdir(self._source_subfolder):
            self.copy(pattern="BSD.txt", dst="licenses")
        if self.settings.os_build == 'Windows':
            self.copy(pattern='*.exe', src=self._source_subfolder, dst='bin', keep_path=False)

    def package_info(self):
        self.env_info.PATH.append(os.path.join(self.package_folder, 'bin'))

    def package_id(self):
        del self.info.settings.compiler
