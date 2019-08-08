#!/usr/bin/env python

from conans import ConanFile, tools, Meson

class LibdrmConan(ConanFile):
    name = "libdrm"
    version = "2.4.96"
    license = "MIT"
    url = "https://gitlab.com/aivero/public/conan/conan-" + name
    description = "Direct Rendering Manager headers and kernel modules"
    settings = "os", "arch", "compiler", "build_type"
    generators = "env"

    def requirements(self):
        self.requires("env-generator/0.1@%s/%s" % (self.user, self.channel))
        self.requires("libpciaccess/0.14@%s/%s" % (self.user, self.channel))

    def source(self):
        tools.get("http://dri.freedesktop.org/libdrm/libdrm-%s.tar.gz" % self.version)

    def build(self):
        args = ["--auto-features=disabled"]
        meson = Meson(self)
        meson.configure(source_folder="%s-%s" % (self.name, self.version), args=args)
        meson.install()

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
