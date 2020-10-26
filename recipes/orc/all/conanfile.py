from build import *


class OrcRecipe(Recipe):
    description = "Optimized Inner Loop Runtime Compiler"
    license = "LGPL-2.1"
    settings = "build_type", "compiler", "arch_build", "os_build", "libc_build", "gstreamer"
    build_requires = ("meson/[^0.55.3]",)

    def source(self):
        self.get(f"https://github.com/GStreamer/orc/archive/{self.version}.tar.gz")

    def build(self):
        args = [
            "-Dtools=enabled",
        ]
        self.meson(args)
