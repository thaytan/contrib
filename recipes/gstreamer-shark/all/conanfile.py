import os

from conans import *


class GstreamerSharkConan(ConanFile):
    description = "GstShark is a front-end for GStreamer traces "
    license = "LGPL"
    settings = {"os": ["Linux"], "arch": ["x86_64", "armv8"]}

    def build_requirements(self):
        self.build_requires("generators/1.0.0")
        self.build_requires("autotools/[^1.0.0]")

    def requirements(self):
        self.requires("gstreamer/[^1.16.0]")
        self.requires("graphviz/[^2.42.1]")

    def source(self):
        tools.get("https://github.com/RidgeRun/gst-shark/archive/v%s.tar.gz" % self.version)
        git = tools.Git(folder=os.path.join("gst-shark-" + self.version, "common"))
        git.clone("git://anongit.freedesktop.org/gstreamer/common", "master")

    def build(self):
        with tools.chdir("gst-shark-" + self.version):
            self.run("sh autogen.sh --disable-gtk-doc")
            autotools = AutoToolsBuildEnvironment(self)
            autotools.configure()
            autotools.install()
