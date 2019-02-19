#!/usr/bin/env python
# -*- coding: utf-8 -*-

from conans import ConanFile, Meson, tools
import os


class GLibConan(ConanFile):
    name = "glib"
    version = "2.58.1"
    default_user = "bincrafters"
    default_channel = "stable"
    description = "GLib provides the core application building blocks for libraries and applications written in C"
    url = "https://github.com/bincrafters/conan-" + name
    author = "BinCrafters <bincrafters@gmail.com>"
    license = "LGPL-2.1"
    exports = ["LICENSE.md"]
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False], "fPIC": [True, False], "pcre": [True, False]}
    default_options = "shared=False", "fPIC=True", "pcre=False"

    def requirements(self):
        self.requires("zlib/1.2.11@%s/%s" % (self.user, self.channel), private=True)
        self.requires("libffi/3.3-rc0@%s/%s" % (self.user, self.channel))
        if self.options.pcre:
            self.requires.add("pcre/8.41@bincraftres/stable")

    def source(self):
        tools.get("https://github.com/GNOME/glib/archive/%s.tar.gz" % self.version)

    def build(self):
        args = ["--libdir=lib", "--auto-features=disabled", "-Dman=False", "-Dgtk_doc=False", "-Dlibmount=False", "-Dselinux=False"]
        if not self.options.pcre:
            args.append("-Dinternal_pcre=False")

        meson = Meson(self)
        meson.configure(source_folder="glib-" + self.version, args=args, pkg_config_paths=os.environ["PKG_CONFIG_PATH"].split(":"))
        meson.build()
        meson.install()

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        for file in os.listdir(os.path.join(self.package_folder, "lib", "pkgconfig")):
            setattr(self.env_info, "PKG_CONFIG_%s_PREFIX" % file[:-3].replace(".", "_").replace("-", "_").upper(), self.package_folder)
        self.env_info.PKG_CONFIG_PATH.append(os.path.join(self.package_folder, "lib", "pkgconfig"))
        self.env_info.PATH.append(os.path.join(self.package_folder, "bin"))
        self.cpp_info.includedirs.append(os.path.join("include", "glib-2.0"))
        self.cpp_info.includedirs.append(os.path.join("include", "gio-unix-2.0"))
        self.cpp_info.includedirs.append(os.path.join("lib", "glib-2.0", "include"))
