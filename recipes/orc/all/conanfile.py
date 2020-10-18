import os
from conans import *


class OrcConan(ConanFile):
    description = "Optimized Inner Loop Runtime Compiler"
    license = "LGPL-2.1"
    settings = "build_type", "compiler", "arch_build", "os_build", "libc_build", "gstreamer"
    build_requires = (
        "cc/[^1.0.0]",
        "meson/[^0.55.3]",
    )

    def source(self):
        tools.get(f"https://github.com/GStreamer/orc/archive/{self.version}.tar.gz")

    def build(self):
        args = [
            "--auto-features=disabled",
            "-Dgtk_doc=disabled",
            "-Dbenchmarks=disabled",
            "-Dexamples=disabled",
        ]
        meson = Meson(self)
        meson.configure(args, source_folder=f"orc-{self.version}", pkg_config_paths=os.environ["PKG_CONFIG_PATH"].split(":"))
        meson.install()
