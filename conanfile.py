from conans import ConanFile, AutoToolsBuildEnvironment, tools
import os

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
    license = "LGPL"
    settings = "os", "compiler", "build_type", "arch"
    generators = "env"

    def build_requirements(self):
        self.build_requires("autotools/[>=1.0.0]@%s/stable" % self.user)

    def requirements(self):
        self.requires("env-generator/[>=1.0.0]@%s/stable" % self.user)
        self.requires("gstreamer/[>=1.16.0]@%s/stable" % self.user)
        self.requires("graphviz/[>=2.42.1]@%s/stable" % self.user)

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

    def package_info(self):
        self.env_info.GST_PLUGIN_PATH.append(os.path.join(self.package_folder, "lib", "gstreamer-1.0"))
