import os
from conans import *


class LibxkbcommonConan(ConanFile):
    description = "Keymap handling library for toolkits and window systems"
    license = "MIT"
    settings = "build_type", "compiler", "arch_build", "os_build", "libc_build"
    build_requires = (
        "meson/[^0.55.3]",
        "bison/[^3.3]",
        "flex/[^2.6.4]",
    )
    requires = (
        "libxcb/[^1.13.1]",
        "libxml2/[^2.9.10]",
    )

    def source(self):
        tools.get(f"https://github.com/xkbcommon/libxkbcommon/archive/xkbcommon-{self.version}.tar.gz")

    def build(self):
        args = [
            "--auto-features=disabled",
            "-Denable-wayland=false",
            "-Denable-docs=false",
        ]
        meson = Meson(self)
        meson.configure(args, source_folder=f"libxkbcommon-xkbcommon-{self.version}", pkg_config_paths=os.environ["PKG_CONFIG_PATH"].split(":"))
        meson.install()
