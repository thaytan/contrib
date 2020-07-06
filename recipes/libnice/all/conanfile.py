import os

from conans import *


class LibNiceConan(ConanFile):
    name = "libnice"
    description = "An implementation of the IETF's Interactive Connectivity Establishment (ICE) standard"
    license = "LGPL"
    settings = {"os_build": ["Linux"], "arch_build": ["x86_64", "armv8"]}
    build_requires = (
        "meson/[^0.51.2]",
    )

    def requirements(self):
        self.requires("glib/[^2.62.0]")
        self.requires("openssl/[^1.1.1b]")
        self.requires(f"gstreamer-plugins-base/[~{self.gst_version}]")

    def source(self):
        tools.get(f"https://github.com/libnice/libnice/archive/{self.version}.tar.gz")

    def build(self):
        args = ["--auto-features=disabled"]
        args.append("-Dgstreamer=" + ("enabled" if self.options.gstreamer else "disabled"))
        meson = Meson(self)
        meson.configure(source_folder=f"{self.name, self.version), args=args}-{pkg_config_paths=os.environ["PKG_CONFIG_PATH"].split(":"}")
        meson.install()
