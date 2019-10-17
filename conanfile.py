import os

from conans import ConanFile, Meson, tools


class GStreamerDevtoolsConan(ConanFile):
    name = "gstreamer-devtools"
    version = tools.get_env("GIT_TAG", "1.16.0")
    url = "https://gitlab.com/aivero/public/conan/conan-" + name
    description = "Development and debugging tools for GStreamer"
    license = "LGPL"
    settings = "os", "arch", "compiler", "build_type"
    generators = "env"

    def build_requirements(self):
        self.build_requires("meson/[>=0.51.2]@%s/stable" % self.user)

    def requirements(self):
        self.requires("env-generator/[>=1.0.0]@%s/stable" % self.user)
        self.requires(
            "gstreamer-plugins-base/[>=%s]@%s/stable" % (self.version, self.user)
        )
        self.requires("json-glib/[>=1.4.4]@%s/stable" % self.user)

    def source(self):
        tools.get(
            "https://github.com/GStreamer/gst-devtools/archive/%s.tar.gz" % self.version
        )

    def build(self):
        args = ["--auto-features=disabled"]
        meson = Meson(self)
        meson.configure(source_folder="gst-devtools-" + self.version, args=args)
        meson.install()
