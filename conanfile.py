#!/usr/bin/env python
# -*- coding: utf-8 -*-

from conans import ConanFile, Meson, tools
import os


class GLibConan(ConanFile):
    name = "glib"
    version = "2.58.1"
    description = "GLib provides the core application building blocks for libraries and applications written in C"
    url = "https://github.com/bincrafters/conan-" + name
    author = "BinCrafters <bincrafters@gmail.com>"
    license = "LGPL-2.1"
    exports = ["LICENSE.md"]
    settings = "os", "arch", "compiler", "build_type"
    options = {"fPIC": [True, False], "with_pcre": [True, False]}
    default_options = "fPIC=True", "with_pcre=False"
    requires = (
        "zlib/1.2.11@conan/stable",
        "libffi/3.3-rc0@bincrafters/stable",
    )
    exports_sources = "dep-fix.patch"

    def requirements(self):
        if self.options.with_pcre:
            self.requires.add("pcre/8.41@bincraftres/stable")

    def source(self):
        tools.get("https://github.com/GNOME/glib/archive/%s.tar.gz" % self.version)
        tools.patch(patch_file="dep-fix.patch", base_path="glib-" + self.version, strip=1)

    def build(self):
        args = ["--libdir=lib", "-Dman=False", "-Dlibmount=False", "-Dselinux=False"]
        meson = Meson(self)
        if not self.options.with_pcre:
            args.append("-Dinternal_pcre=False")
        meson.configure(source_folder="glib-" + self.version, args=args, pkg_config_paths=os.environ["PKG_CONFIG_PATH"].split(":"))
        meson.build()
        meson.install()

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        self.env_info.PKG_CONFIG_PATH.append(os.path.join(self.package_folder, "lib", "pkgconfig"))
        self.env_info.PATH.append(os.path.join(self.package_folder, "bin"))
        self.cpp_info.includedirs.append(os.path.join("include", "glib-2.0"))
        self.cpp_info.includedirs.append(os.path.join("lib", "glib-2.0", "include"))
        self.cpp_info.includedirs.append(os.path.join("include", "gio-unix-2.0"))
