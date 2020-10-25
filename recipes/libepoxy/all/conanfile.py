import os
from conans import *


class LibepoxyConan(ConanFile):
    description = "Library handling OpenGL function pointer management"
    license = "MIT"
    settings = "build_type", "compiler", "arch_build", "os_build", "libc_build"
    options = {
        "x11": [True, False],
    }
    default_options = ("x11=True",)
    build_requires = ("meson/[^0.55.3]",)
    requires = ("mesa/[^20.2.1]",)

    def requirements(self):
        if self.options.x11:
            self.requires("libx11/[^1.6.8]")

    def source(self):
        tools.get(f"https://github.com/anholt/libepoxy/archive/{self.version}.tar.gz")

    def build(self):
        args = [
            "--auto-features=disabled",
            "-Dglx=yes",
            "-Dtests=false",
            f"-Dx11={self.options.x11}",
        ]
        meson = Meson(self)
        meson.configure(args, source_folder=f"libepoxy-{self.version}", pkg_config_paths=os.environ["PKG_CONFIG_PATH"].split(":"))
        meson.install()
