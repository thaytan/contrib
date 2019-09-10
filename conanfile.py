from conans import ConanFile, Meson, tools
import os

def get_version():
    git = tools.Git()
    try:
        tag = git.get_tag()
        return tag if tag else "1.16.0"
    except:
        return None

class GStreamerPythonConan(ConanFile):
    name = "gstreamer-python"
    version = get_version()
    url = "https://gitlab.com/aivero/public/conan/conan-" + name
    description = "Gstreamer Python bindings"
    license = "https://gitlab.freedesktop.org/gstreamer/gstreamer/raw/master/COPYING"
    settings = "os", "arch", "compiler", "build_type"
    generators = "env"

    def requirements(self):
        self.requires("env-generator/0.1@%s/stable" % self.user)
        self.requires("gstreamer/%s@%s/stable" % (self.version, self.user))
        self.requires("gobject-introspection/1.59.3@%s/stable" % self.user)
        self.requires("python-gobject/3.33.1@%s/stable" % self.user)

    def source(self):
        tools.get("https://github.com/GStreamer/gst-python/archive/%s.tar.gz" % self.version)

    def build(self):
        args = ["--auto-features=disabled"]
        meson = Meson(self)
        meson.configure(source_folder="gst-python-" + self.version, args=args)
        meson.install()

    def package(self):
        if self.settings.build_type == "Debug":
            self.copy("*.c", "src")
            self.copy("*.h", "src")

    def package_info(self):
        self.cpp_info.srcdirs.append("src")
        self.env_info.PYTHONPATH = os.path.join(self.package_folder, "lib", "python3.6", "site-packages")
