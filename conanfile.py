import os

from conans import ConanFile, Meson, tools


class GStreamerPythonConan(ConanFile):
    name = "gstreamer-python"
    version = tools.get_env("GIT_TAG", "1.16.0")
    url = "https://gitlab.com/aivero/public/conan/conan-" + name
    description = "Gstreamer Python bindings"
    license = "https://gitlab.freedesktop.org/gstreamer/gstreamer/raw/master/COPYING"
    settings = "os", "arch", "compiler", "build_type"

    def build_requirements(self):
        self.build_requires("generators/1.0.0@%s/stable" % self.user)

    def requirements(self):
        self.requires("gstreamer/%s@%s/stable" % (self.version, self.user))
        self.requires("gobject-introspection/1.59.3@%s/stable" % self.user)
        self.requires("python-gobject/3.33.1@%s/stable" % self.user)

    def source(self):
        tools.get("https://github.com/GStreamer/gst-python/archive/%s.tar.gz" % self.version)

    def build(self):
        args = ["--auto-features=disabled"]
        meson = Meson(self)
        meson.configure(source_folder="gst-python-" + self.version, args=args, pkg_config_paths=os.environ["PKG_CONFIG_PATH"].split(":"))
        meson.install()

    def package_info(self):
        self.env_info.PYTHONPATH = os.path.join(self.package_folder, "lib", "python3.7", "site-packages")
