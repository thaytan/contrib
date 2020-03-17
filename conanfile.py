import os
import shutil

from conans import ConanFile, Meson, tools, CMake, AutoToolsBuildEnvironment


class GStreamerPerfConan(ConanFile):
    name = "gst-perf"
    version = tools.get_env("GIT_TAG", "1.16.0")
    description = "Performance Evaluation tool for Gstreamer"
    license = "LGPL"
    settings = "os", "arch", "compiler", "build_type"
    scm = {
        "type": "git",
        "url": "https://github.com/RidgeRun/gst-perf",
        "revision": "master",
        "recursive": True,
        "subfolder": ("gst-perf-" + version)
    }

    def requirements(self):
        self.requires("glib/[>=2.62.0]@%s/stable" % self.user) 
        self.requires("gstreamer/[>=%s]@%s/stable" % (self.version,self.user)) 

    def build_requirements(self):
        self.build_requires("generators/[>=1.0.0]@%s/stable" % self.user) 
        self.build_requires("autotools/[>=1.0.0]@%s/stable" % self.user) 
        self.build_requires("automake/[>=1.16.1]@%s/stable" % self.user) 
        self.build_requires("autoconf/[>=2.69]@%s/stable" % self.user) 

    def source(self):
        git = tools.Git(folder="src/gst-perf-" + self.version)
        git.clone("https://github.com/RidgeRun/gst-perf.git", "master")
        os.rename("%s-%s" % (self.name, self.version), "sources")

    def build(self):
        with tools.chdir("sources"):
            self.run("sh autogen.sh")
            autotools = AutoToolsBuildEnvironment(self)
            autotools.configure()
            autotools.make()
            autotools.install()
