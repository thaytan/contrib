#!/usr/bin/env python

from conans import ConanFile, tools, Meson
import os


class LibdrmConan(ConanFile):
    name            = "libdrm"
    version         = "2.4.96"
    license         = "MIT"
    default_user    = "bincrafters"
    default_channel = "stable"
    url             = "https://github.com/prozum/conan-libdrm.git"
    description     = "Direct Rendering Manager headers and kernel modules"
    settings = "os", "arch", "compiler", "build_type"

    def requirements(self):
        self.requires("libpciaccess/0.14@%s/%s" % (self.user, self.channel))

    def source(self):
        tools.get("http://dri.freedesktop.org/libdrm/libdrm-%s.tar.gz" % self.version)

    def build(self):
        args = ["--auto-features=disabled"]
        meson = Meson(self)
        meson.configure(source_folder="libdrm-" + self.version, args=args, pkg_config_paths=os.environ['PKG_CONFIG_PATH'].split(":"))
        meson.build()
        meson.install()

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        self.env_info.PKG_CONFIG_PATH.append(os.path.join(self.package_folder, "lib", "pkgconfig"))
        for file in os.listdir(os.path.join(self.package_folder, "lib", "pkgconfig")):
            setattr(self.env_info, "PKG_CONFIG_%s_PREFIX" % file[:-3].replace(".", "_").replace("-", "_").upper(), self.package_folder)
