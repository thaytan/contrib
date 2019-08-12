#!/usr/bin/env python
# -*- coding: utf-8 -*-

from conans import ConanFile, Meson, tools
import os

class GLibConan(ConanFile):
    name = "glib"
    version = "2.58.1"
    description = "GLib provides the core application building blocks for libraries and applications written in C"
    url = "https://gitlab.com/aivero/public/conan/conan-" + name
    license = "LGPL-2.1"
    settings = "os", "arch", "compiler", "build_type"
    generators = "env"

    def requirements(self):
        self.requires("env-generator/0.1@%s/%s" % (self.user, self.channel))
        self.requires("zlib/1.2.11@%s/%s" % (self.user, self.channel))
        self.requires("libffi/3.3-rc0@%s/%s" % (self.user, self.channel))

    def source(self):
        tools.get("https://github.com/GNOME/glib/archive/%s.tar.gz" % self.version)

    def build(self):
        args = ["--auto-features=disabled", "-Dman=False", "-Dgtk_doc=False", "-Dlibmount=False", "-Dselinux=False", "-Dinternal_pcre=False"]
        meson = Meson(self)
        meson.configure(source_folder="%s-%s" % (self.name, self.version), args=args)
        meson.install()

    def package(self):
        if self.settings.build_type == "Debug":
            self.copy("*.c", "src")
            self.copy("*.h", "src")

    def package_info(self):
        self.cpp_info.includedirs.append(os.path.join("include", "gio-unix-2.0"))
        self.cpp_info.includedirs.append(os.path.join("include", "glib-2.0"))
        self.cpp_info.includedirs.append(os.path.join("lib", "glib-2.0", "include"))
        self.cpp_info.libs = tools.collect_libs(self)
        self.cpp_info.srcdirs.append("src")
