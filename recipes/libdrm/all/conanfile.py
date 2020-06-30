import os

from conans import *


class LibdrmConan(ConanFile):
    description = "Direct Rendering Manager headers and kernel modules"
    license = "MIT"
    settings = {"os": ["Linux"], "arch": ["x86_64", "armv8"]}
    build_requires = (
        "generators/1.0.0",
        "meson/[^0.51.2]",
    )
    requires = ("libpciaccess/[^0.14]",)

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
