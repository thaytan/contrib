#!/usr/bin/env python
# -*- coding: utf-8 -*-

from conans import ConanFile, Meson, tools
import os


class GLibConan(ConanFile):
    name = "glib-2.0"
    version = "2.58.1"
    description = "GLib provides the core application building blocks for libraries and applications written in C"
    url = "https://github.com/bincrafters/conan-" + name
    homepage = "https://github.com/GNOME/glib"
    author = "BinCrafters <bincrafters@gmail.com>"
    license = "LGPL-2.1"
    exports = ["LICENSE.md"]
    settings = "os", "arch", "compiler", "build_type"
    options = {"fPIC": [True, False], "with_pcre": [True, False]}
    default_options = "fPIC=True", "with_pcre=False"
    requires = "libffi/3.2.1@bincrafters/stable", "zlib/1.2.11@conan/stable"
    source_subfolder = "source"
    build_subfolder = "build"
    generators = "pkg_config"
    args = ['-Dman=False', '-Ddoc=False', '-Dlibmount=False', '-Dselinux=False']
    lib_targets = [
        ("glib-2.0", ["glib"]),
    ]
    custom_targets = [
    ]

    def requirements(self):
        if self.options.with_pcre:
            self.requires.add("pcre/8.41@bincraftres/stable")

    def source(self):
        tools.get("{0}/archive/{1}.tar.gz".format(self.homepage, self.version))
        os.rename("glib-" + self.version, self.source_subfolder)

    def _configure_meson(self):
        meson = Meson(self)
        self.args.append('--default-library=shared')
        if not self.options.with_pcre:
            self.args.append('-Dinternal_pcre=False')
        meson.configure(source_folder=self.source_subfolder, build_folder=self.build_subfolder, args=self.args)
        return meson

    def _lib_name(self, lib):
        return "lib%s.so.0.%s00.%s" % (lib[0], self.version.split(".")[1], self.version.split(".")[2])

    def _lib_path(self, lib):
        path = lib[1] + [self._lib_name(lib)]
        return os.path.join(*path)

    def build(self):
        self.meson = self._configure_meson()
        targets = list(map(self._lib_path, self.lib_targets))
        targets += self.custom_targets
        self.meson.build(build_dir=self.build_subfolder, targets=targets)

    def package(self):
        self.copy("*glib-mkenums", src=self.build_subfolder + "/gobject", dst="bin", keep_path=False)
        for target in self.lib_targets + self.custom_targets:
            self.copy("*lib" + target[0] + ".so*", dst="lib", keep_path=False, symlinks=True)
        for target in self.custom_targets:
            self.copy("*" + target[0], dst="lib", keep_path=False)
        self.copy("*.h", dst="include/glib",
                  src=self.source_subfolder + "/glib",
                  excludes="glib.h")
        self.copy("glib.h", dst="include",
                  src=self.source_subfolder + "/glib",
                  keep_path=False)
        self.copy("glib-unix.h", dst="include",
                  src=self.source_subfolder + "/glib",
                  keep_path=False)
        self.copy("glibconfig.h", dst="include",
                  src=self.build_subfolder + "/glib",
                  keep_path=False)

    def package_info(self):
        self.cpp_info.libs = [self.name]
        if self.settings.os == "Linux":
            self.cpp_info.libs.append("pthread")
        self.env_info.PATH.append(os.path.join(self.package_folder, "bin"))
