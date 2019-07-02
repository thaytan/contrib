import os
from conans import ConanFile, AutoToolsBuildEnvironment, tools
from conans.util import files


class GstreamerSharkConan(ConanFile):
    version = "0.6.1"
    name = "gstreamer-shark"
    license = "https://raw.githubusercontent.com/strukturag/libde265/master/COPYING"
    description = "GstShark is a front-end for GStreamer traces "
    default_user = "bincrafters"
    default_channel = "stable"
    url = "https://github.com/RidgeRun/gst-shark"
    settings = "os", "compiler", "build_type", "arch"
    scm = {
        "type": "git",
        "url": "https://github.com/RidgeRun/gst-shark/",
        "revision": "master",
        "recursive": True
    }

    def requirements(self):
        self.requires("gstreamer/1.16.0@%s/%s" % (self.user, self.channel))
        self.requires("graphviz/2.40.1@%s/%s" % (self.user, self.channel))

    def build(self):
        vars = {
            "CFLAGS": "-fdebug-prefix-map=%s=." % self.source_folder,
        }
        with tools.environment_append(vars):
                self.run("./autogen.sh --disable-gtk-doc")
                autotools = AutoToolsBuildEnvironment(self)
                autotools.configure()
                autotools.make()
                autotools.make(args=["install"])

    def package(self):
        if self.channel == "testing":
            self.copy("*.c", "src")
            self.copy("*.h", "src")

    def package_info(self):
        self.env_info.GST_PLUGIN_PATH.append(os.path.join(self.package_folder, "lib", "gstreamer-1.0"))
        self.env_info.SOURCE_PATH.append(os.path.join(self.package_folder, "src"))
        self.cpp_info.srcdirs.append("src")
