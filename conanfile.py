#!/usr/bin/env python
# -*- coding: utf-8 -*-

from conans import ConanFile, tools, AutoToolsBuildEnvironment
import os


class LibnameConan(ConanFile):
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

    def build(self):
        args = ['prefix=%s' % self.package_folder,]

        with tools.chdir('sources'):
            env_build = AutoToolsBuildEnvironment(self)
            env_build.configure(args=args)
            env_build.make()
            env_build.make(args=['install'])

    def package(self):
        with tools.chdir("sources"):
            self.copy(pattern="BSD.txt")

    def package_info(self):
        self.env_info.PATH.append(os.path.join(self.package_folder, 'bin'))
