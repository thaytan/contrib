#!/usr/bin/env python

from conans import ConanFile, tools, Meson
import os


class IntelVaapiDriverConan(ConanFile):
    name = "intel-vaapi-driver"
    version = "2.3.0"
    license = "MIT"
    url = "https://gitlab.com/aivero/public/conan/conan-" + name
    description = "VA-API user mode driver for Intel GEN Graphics family"
    settings = "os", "arch", "compiler", "build_type"
    generators = "env"

    def requirements(self):
        self.requires("env-generator/0.1@%s/%s" % (self.user, self.channel))
        self.requires("libdrm/2.4.96@%s/%s" % (self.user, self.channel))
        self.requires("libva/2.3.0@%s/%s" % (self.user, self.channel))

    def source(self):
        tools.get("https://github.com/intel/intel-vaapi-driver/archive/%s.tar.gz" % self.version)

    def build(self):
        args = ["-Ddriverdir=" + os.path.join(self.package_folder, "lib", "dri")]
        meson = Meson(self)
        meson.configure(source_folder="intel-vaapi-driver-" + self.version, args=args)
        meson.install()

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        self.env_info.LIBVA_DRIVERS_PATH.append(os.path.join(self.package_folder, "lib", "dri"))
