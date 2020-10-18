import os

from conans import *


class LibdrmConan(ConanFile):
    description = "Direct Rendering Manager headers and kernel modules"
    license = "MIT"
    settings = "build_type", "compiler", "arch_build", "os_build", "libc_build"
    build_requires = (
        "meson/[^0.51.2]",
    )
    requires = (
        "base/[^1.0.0]",
        "libpciaccess/[^0.14]",
    )

    def source(self):
        tools.get(f"http://dri.freedesktop.org/libdrm/libdrm-{self.version}.tar.gz")

    def build(self):
        args = [
            "--auto-features=disabled",
            "-Dradeon=false",
            "-Damdgpu=false",
            "-Dnouveau=true",
        ]
        meson = Meson(self)
        meson.configure(source_folder=f"{self.name, self.version), args=args}-{pkg_config_paths=os.environ["PKG_CONFIG_PATH"].split(":"}")
        meson.install()
