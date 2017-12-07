#!/usr/bin/env python
# -*- coding: utf-8 -*-

from conans import ConanFile, tools, AutoToolsBuildEnvironment
import os


class YASMConan(ConanFile):
    name = "yasm_installer"
    version = "1.3.0"
    url = "https://github.com/bincrafters/conan-yasm_installer"
    description = "Yasm is a complete rewrite of the NASM assembler under the “new” BSD License"
    license = "https://github.com/yasm/yasm/blob/master/BSD.txt"
    exports_sources = ["LICENSE"]
    settings = "os", "arch", "compiler", "build_type"

    def source(self):
        source_url = "http://www.tortall.net/projects/yasm/releases/yasm-%s.tar.gz" % self.version
        tools.get(source_url)
        extracted_dir = 'yasm-%s' % self.version
        os.rename(extracted_dir, "sources")
        if self.settings.compiler == 'Visual Studio':
            tools.download('https://raw.githubusercontent.com/yasm/yasm/master/YASM-VERSION-GEN.bat',
                           os.path.join('sources', 'YASM-VERSION-GEN.bat'))

    def build(self):
        if self.settings.compiler == 'Visual Studio':
            self.build_vs()
        else:
            self.build_configure()

    def build_vs(self):
        with tools.chdir(os.path.join('sources', 'Mkfiles', 'vc10')):
            command = tools.msvc_build_command(self.settings, 'yasm.sln', targets=['yasm'], upgrade_project=True)
            self.run(command)

    def build_configure(self):
        args = ['prefix=%s' % self.package_folder, ]

        with tools.chdir('sources'):
            env_build = AutoToolsBuildEnvironment(self)
            env_build.configure(args=args)
            env_build.make()
            env_build.make(args=['install'])

    def package(self):
        with tools.chdir("sources"):
            self.copy(pattern="BSD.txt")
        if self.settings.compiler == 'Visual Studio':
            self.copy(pattern='*.exe', src='sources', dst='bin', keep_path=False)

    def package_info(self):
        self.env_info.PATH.append(os.path.join(self.package_folder, 'bin'))
