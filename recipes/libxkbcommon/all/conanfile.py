import os

from conans import *


class LibxcbConan(ConanFile):
    description = "Keymap handling library for toolkits and window systems"
    license = "MIT"
    settings = "build_type", "compiler", "arch_build", "os_build", "libc_build"
    build_requires = (
        "meson/[^0.51.2]",
        "bison/[^3.3]",
        "flex/[^2.6.4]",
    )
    requires = (
        "base/[^1.0.0]",
        "libxcb/[^1.13.1]",
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
        meson.configure(source_folder="libxkbcommon-xkbcommon-" + self.version, args=args, pkg_config_paths=os.environ["PKG_CONFIG_PATH"].split(":"))
        meson.install()
