#!/usr/bin/env python
# -*- coding: utf-8 -*-

from conans import ConanFile, CMake, tools
import os

def get_version():
    git = tools.Git()
    try:
        if (git.get_tag() == None):
            return "master"
        else:
            return git.get_tag()
    except:
        return None

class DepthMetaConan(ConanFile):
    name = "gstreamer-depth-meta"
    version = get_version()
    description = "Library to stream depth video"
    url = "https://aivero.com"
    default_user = "aivero"
    default_channel = "stable"
    settings = "os", "arch", "compiler", "build_type"
    generators = "cmake", "virtualenv", "virtualrunenv"
    exports_sources = ["CMakeLists.txt", "src/*"]

    def requirements(self):
        self.requires("gstreamer/1.15.1@%s/%s" % (self.user, self.channel))
        self.requires("gstreamer-plugins-base/1.15.1@%s/%s" % (self.user, self.channel))

    def build(self):
        vars = {
            "CFLAGS": "-fdebug-prefix-map=%s=." % self.source_folder,
            "CXXFLAGS": "-fdebug-prefix-map=%s=." % self.source_folder,
        }
        with tools.environment_append(vars):
            cmake = CMake(self)
            cmake.configure()
            cmake.build()
            cmake.install()

    def package(self):
        if self.channel == "testing":
            self.copy("meta-*.c", "src")
            self.copy("meta-*.h", "src")

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        for lib_path in self.deps_cpp_info.lib_paths:
            self.env_info.LD_LIBRARY_PATH.append(lib_path)
        self.env_info.PATH.append(os.path.join(self.package_folder, "bin"))
        self.env_info.SOURCE_PATH.append(os.path.join(self.package_folder, "src"))
        self.env_info.PKG_CONFIG_PATH.append(os.path.join(self.package_folder, "lib", "pkgconfig"))
        for file in os.listdir(os.path.join(self.package_folder, "lib", "pkgconfig")):
            setattr(self.env_info, "PKG_CONFIG_%s_PREFIX" % file[:-3].replace(".", "_").replace("-", "_").upper(), self.package_folder)
        self.cpp_info.srcdirs.append("src")
