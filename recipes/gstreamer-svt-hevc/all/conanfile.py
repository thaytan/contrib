import os

from conans import ConanFile, Meson, tools


class GStreamerSvtHevcConan(ConanFile):
    description = "The Scalable Video Technology for HEVC Encoder GStreamer plugin"
    license = "LGPL"
    settings = "os", "arch", "compiler", "build_type"

    def build_requirements(self):
        self.build_requires("generators/[>=1.0.0]@%s/stable" % self.user)
        self.build_requires("meson/[>=0.51.2]@%s/stable" % self.user)

    def requirements(self):
        self.requires("gstreamer-plugins-base/[>=1.16.2]@%s/stable" % self.user)
        self.requires("svt-hevc/[>=1.4.3]@%s/stable" % self.user)

    def source(self):
        tools.get(
            "https://github.com/OpenVisualCloud/SVT-HEVC/archive/v%s.tar.gz"
            % self.version
        )

    def build(self):
        args = ["--auto-features=disabled"]
        meson = Meson(self)
        meson.configure(source_folder="SVT-HEVC-%s/gstreamer-plugin" % self.version)
        meson.install()

    def package_info(self):
        self.env_info.GST_PLUGIN_PATH.append(
            os.path.join(self.package_folder, "lib", "gstreamer-1.0")
        )
