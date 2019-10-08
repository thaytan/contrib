import os
from conans import ConanFile, AutoToolsBuildEnvironment, tools
from conans.util import files

def get_version():
    git = tools.Git()
    try:
        tag = git.get_tag()
        return tag if tag else "0.6.1"
    except:
        return None

class GstreamerSharkConan(ConanFile):
    name = "gstreamer-shark"
    version = get_version()
    description = "GstShark is a front-end for GStreamer traces "
    url = "https://gitlab.com/aivero/public/conan/conan-" + name
    license = "https://raw.githubusercontent.com/strukturag/libde265/master/COPYING"
    settings = "os", "compiler", "build_type", "arch"
    scm = {
        "type": "git",
        "url": "https://github.com/RidgeRun/gst-shark/",
        "revision": "master",
        "recursive": True
    }
    generators = "env"
    
    def build_requirements(self):
        self.build_requires("autotools/[>=1.0.0]@%s/stable" % self.user)

    def requirements(self):
        self.requires("env-generator/[>=1.0.0]@%s/stable" % self.user)
        self.requires("gstreamer/[>=1.16.0]@%s/stable" % self.user)
        self.requires("graphviz/[>=2.40.1]@%s/stable" % self.user)

    def build(self):
        self.run("./autogen.sh --disable-gtk-doc")
        autotools = AutoToolsBuildEnvironment(self)
        autotools.configure()
        autotools.install()

    def package(self):
        if self.settings.build_type == "Debug":
            self.copy("*.c", "src")
            self.copy("*.h", "src")

    def package_info(self):
        self.env_info.GST_PLUGIN_PATH.append(os.path.join(self.package_folder, "lib", "gstreamer-1.0"))
        self.cpp_info.srcdirs.append("src")
