import os
import shutil

from conans import ConanFile, Meson, tools, CMake, AutoToolsBuildEnvironment


class GStreamerPerfConan(ConanFile):
    name = "gst-perf"
    version = tools.get_env("GIT_TAG", "0.2.3")
    description = "Performance Evaluation tool for Gstreamer"
    license = "LGPL"
    settings = "os", "arch", "compiler", "build_type"


    def requirements(self):
        self.requires("glib/[>=2.62.0]@%s/stable" % self.user)
        self.requires("gstreamer/[>=%s]@%s/stable" % (self.version,self.user))

    def build_requirements(self):
        self.build_requires("generators/[>=1.0.0]@%s/stable" % self.user)
        self.build_requires("autotools/[>=1.0.0]@%s/stable" % self.user)
        self.build_requires("automake/[>=1.16.1]@%s/stable" % self.user)
        self.build_requires("autoconf/[>=2.69]@%s/stable" % self.user)

    def source(self):
        git = tools.Git()
        git.clone("https://github.com/RidgeRun/gst-perf.git", "v%s" % self.version)

    def build(self):
        self.run("sh autogen.sh")
        autotools = AutoToolsBuildEnvironment(self)
        autotools.configure()
        autotools.make()
        autotools.install()
