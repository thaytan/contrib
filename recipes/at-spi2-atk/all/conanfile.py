import os
from conans import *


class AtSpi2AtkConan(ConanFile):
    description = "A GTK+ module that bridges ATK to D-Bus at-spi"
    license = "LGPL"
    settings = "build_type", "compiler", "arch_build", "os_build", "libc_build"
    build_requires = ("meson/[^0.55.3]",)
    requires = (
        "atk/[^2.36.0]",
        "at-spi2-core/[^2.38.0]",
        "libxml2/[^2.9.9]",
    )

    def source(self):
        version = self.version.replace(".", "_")
        tools.get(f"https://gitlab.gnome.org/GNOME/at-spi2-atk/-/archive/AT_SPI2_ATK_{version}/at-spi2-atk-AT_SPI2_ATK_{version}.tar.bz2")

    def build(self):
        args = ["--auto-features=disabled", "--wrap-mode=nofallback"]
        meson = Meson(self)
        meson.configure(args, source_folder=f"at-spi2-atk-AT_SPI2_ATK_{self.version.replace('.', '_')}", pkg_config_paths=os.environ["PKG_CONFIG_PATH"].split(":"))
        meson.install()
