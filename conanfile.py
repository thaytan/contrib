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
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = "shared=False", "fPIC=True"
    folder_name = name + "-" + version
    no_copy_source = True

    def requirements(self):
        self.requires("zlib/1.2.11@%s/%s" % (self.user, self.channel))
        self.requires("libffi/3.3-rc0@%s/%s" % (self.user, self.channel))

    def source(self):
        tools.get("https://github.com/GNOME/glib/archive/%s.tar.gz" % self.version)

    def build(self):
        args = ["--libdir=lib", "--auto-features=disabled", "-Dman=False", "-Dgtk_doc=False", "-Dlibmount=False", "-Dselinux=False", "-Dinternal_pcre=False"]
        meson = Meson(self)
        meson.configure(source_folder=self.folder_name, build_folder="build", args=args, pkg_config_paths=os.environ["PKG_CONFIG_PATH"].split(":"))
        meson.build()
        meson.install()

    def package(self):
        if self.channel == "testing":
            self.copy("*", "src", self.folder_name)

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        for file in os.listdir(os.path.join(self.package_folder, "lib", "pkgconfig")):
            setattr(self.env_info, "PKG_CONFIG_%s_PREFIX" % file[:-3].replace(".", "_").replace("-", "_").upper(), self.package_folder)
        self.env_info.PKG_CONFIG_PATH.append(os.path.join(self.package_folder, "lib", "pkgconfig"))
        self.env_info.PATH.append(os.path.join(self.package_folder, "bin"))
        self.cpp_info.includedirs.append(os.path.join("include", "glib-2.0"))
        self.cpp_info.includedirs.append(os.path.join("include", "gio-unix-2.0"))
        self.cpp_info.includedirs.append(os.path.join("lib", "glib-2.0", "include"))
        self.cpp_info.srcdirs.append("src")
