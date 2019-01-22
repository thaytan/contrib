#!/usr/bin/env python

from conans import ConanFile, tools, Meson
import os


class LibdrmConan(ConanFile):
    name            = "libdrm"
    version         = "2.4.96"
    license         = "MIT"
    url             = "https://github.com/prozum/conan-libdrm.git"
    description     = "Direct Rendering Manager headers and kernel modules"
    settings = "os", "arch", "compiler", "build_type"
    requires = "libpciaccess/0.14@bincrafters/stable",

    def source(self):
        tools.get("http://dri.freedesktop.org/libdrm/libdrm-%s.tar.gz" % self.version)

    def build(self):
        args = ["--libdir=lib"]
        meson = Meson(self)
        meson.configure(source_folder="libdrm-" + self.version, args=args, pkg_config_paths=os.environ['PKG_CONFIG_PATH'].split(":"))
        meson.build()
        meson.install()

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        self.env_info.PKG_CONFIG_PATH.append(os.path.join(self.package_folder, "lib", "pkgconfig"))
