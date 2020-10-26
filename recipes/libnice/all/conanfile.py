from build import *


class LibNiceRecipe(Recipe):
    description = "An implementation of the IETF's Interactive Connectivity Establishment (ICE) standard"
    license = "LGPL"
    settings = "build_type", "compiler", "arch_build", "os_build", "libc_build", "gstreamer"
    build_requires = ("meson/[^0.55.3]",)
    requires = ("openssl1/[^1.1.1h]",)

    def build_requirements(self):
        self.build_requires(f"gstreamer-plugins-base/[~{self.settings.gstreamer}]")

    def source(self):
        self.get(f"https://github.com/libnice/libnice/archive/{self.version}.tar.gz")

    def build(self):
        args = [
            "--auto-features=disabled",
            "-Dgstreamer=enabled",
        ]
        self.meson(args)
