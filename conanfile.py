from conans import ConanFile, Meson, tools
import os

def get_version():
    git = tools.Git()
    try:
        tag = git.get_tag()
        return tag if tag else "1.16.0"
    except:
        return None

class GStreamerVaapiConan(ConanFile):
    name = "gstreamer-vaapi"
    version = get_version()
    url = "https://gitlab.com/aivero/public/conan/conan-" + name
    description = "Hardware-accelerated video decoding, encoding and processing on Intel graphics through VA-API"
    license = "LGPL"
    settings = "os", "arch", "compiler", "build_type"
    generators = "env"

    def build_requirements(self):
        self.build_requires("env-generator/[>=0.1]@%s/stable" % self.user)

    def requirements(self):
        self.requires("glib/[>=2.58.1]@%s/stable" % self.user)
        self.requires("gstreamer-plugins-base/[>=%s]@%s/stable" % (self.version, self.user))
        self.requires("gstreamer-plugins-bad/[>=%s]@%s/stable" % (self.version, self.user))
        self.requires("libva/[>=2.3.0]@%s/stable" % self.user)

    def source(self):
        tools.get("https://github.com/GStreamer/gstreamer-vaapi/archive/%s.tar.gz" % self.version)

    def build(self):
        args = ["--auto-features=disabled"]
        meson = Meson(self)
        meson.configure(source_folder="gstreamer-vaapi-" + self.version)
        meson.install()

    def package(self):
        if self.settings.build_type == "Debug":
            self.copy("*.c", "src")
            self.copy("*.h", "src")

    def package_info(self):
        self.env_info.GST_PLUGIN_PATH.append(os.path.join(self.package_folder, "lib", "gstreamer-1.0"))
