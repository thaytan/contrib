#!/usr/bin/env python

import os
from conans import ConanFile, AutoToolsBuildEnvironment, tools


class LibPciAccessConan(ConanFile):
    name = "libpciaccess"
    version = "0.14"
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False]}
    default_options = "shared=False",
    homepage = "https://github.com/freedesktop/xorg-libpciaccess"
    default_user = "bincrafters"
    url = "http://github.com/bincrafters/conan-libusb"
    author = "Bincrafters <bincrafters@gmail.com>"
    license = "MIT"
    description = "Generic PCI access library"
    source_subfolder = "source_subfolder"
    exports = ["LICENSE.md"]

    def requirements(self):
        self.requires("xorg-util-macros/1.19.1@%s/stable" % self.user)

    def source(self):
        tools.get("https://github.com/freedesktop/xorg-libpciaccess/archive/libpciaccess-%s.tar.gz" % self.version)
        os.rename("xorg-libpciaccess-libpciaccess-%s" % self.version, self.source_subfolder)

    def build(self):
        configure_args = ['--enable-shared' if self.options.shared else '--disable-shared']
        configure_args.append('--enable-static' if not self.options.shared else '--disable-static')
        env_build = AutoToolsBuildEnvironment(self)
        with tools.chdir(self.source_subfolder):
            self.run("autoreconf -i")
            env_build.configure(pkg_config_paths=os.environ['PKG_CONFIG_PATH'].split(":"))
            env_build.make()
            env_build.make(args=["install"])

    def package(self):
        self.copy("COPYING", src=self.source_subfolder, dst="licenses", keep_path=False)

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        self.env_info.PKG_CONFIG_PATH.append(os.path.join(self.package_folder, "lib", "pkgconfig"))
