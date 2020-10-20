import os
from conans import *


class LibdrmConan(ConanFile):
    description = "Direct Rendering Manager headers and kernel modules"
    license = "MIT"
    settings = "build_type", "compiler", "arch_build", "os_build", "libc_build"
    build_requires = (
        "cc/[^1.0.0]",
        "meson/[^0.55.3]",
        "libpciaccess/[>=0.16]",
    )

    def source(self):
        tools.get(f"http://dri.freedesktop.org/libdrm/libdrm-{self.version}.tar.xz")

    def build(self):
        args = [
            "--auto-features=disabled",
            "-Dradeon=false",
            "-Damdgpu=true",
            "-Dnouveau=true",
        ]
        meson = Meson(self)
        meson.configure(args, source_folder=f"libdrm-{self.version}", pkg_config_paths=os.environ["PKG_CONFIG_PATH"].split(":"))
        meson.install()
