#!/usr/bin/env python
# -*- coding: utf-8 -*-
from conans import ConanFile, CMake, tools

def get_version():
    git = tools.Git()
    try:
        if git.get_tag():
            return git.get_tag()
        else:
            return git.get_branch()
    except:
        return None

def get_upper_version_bound(version, version_diff="0.1.0"):
    try:
        v = tools.Version(version)
    except:
        print("Input version is not a valid SemVer")
    try:
        v_diff = tools.Version(version_diff)
        version_out = "%d.%d.%d" % ((int(v.major) + int(v_diff.major)),(int(v.minor) + int(v_diff.minor)), (int(v.patch) + int(v_diff.patch)))
        if v.prerelease:
            version_out = version_out + "-" + v.prerelease
        elif v_diff.prerelease:
            version_out = version_out + "-" + v_diff.prerelease
        return version_out
    except Exception as e:
        print(e)
        print("Version diff is not a valid SemVer")

class DepthMetaConan(ConanFile):
    name = "gstreamer-depth-meta"
    license = "Apache 2.0"
    version = get_version()
    description = "Library to stream depth video"
    url = "https://aivero.com"
    settings = "os", "arch", "compiler", "build_type"
    exports_sources = ["CMakeLists.txt", "src/*"]
    generators = "env"

    def build_requirements(self):
        self.build_requires("cmake/[>=3.15.3]@%s/stable" % (self.user))

    def requirements(self):
        self.requires("env-generator/[>=1.0.0]@%s/stable" % self.user)
        gst_version = "1.16.0"
        gst_upper_version_bound = get_upper_version_bound(gst_version)
        # self.requires("gstreamer/[>=%s <%s]@%s/stable" % (gst_version, gst_upper_version_bound, self.user))
        self.requires("gstreamer-plugins-base/[>=%s <%s]@%s/stable" % (gst_version, gst_upper_version_bound, self.user))

    def build(self):
        env = {
            "GIT_PKG_VER": "%s" % self.version,
        }
        with tools.environment_append(env):
            cmake = CMake(self)
            cmake.configure()
            cmake.install()

    def package(self):
        if self.settings.build_type == "Debug":
            self.copy("*-meta.c", "src")
            self.copy("*-meta.h", "src")

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        self.cpp_info.srcdirs.append("src")
