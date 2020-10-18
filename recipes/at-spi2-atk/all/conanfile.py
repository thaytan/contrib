import os

from conans import *


class AtSpi2AtkConan(ConanFile):
    description = "A GTK+ module that bridges ATK to D-Bus at-spi"
    license = "LGPL"
    settings = "build_type", "compiler", "arch_build", "os_build", "libc_build"
    build_requires = (
        "meson/[^0.51.2]",
    )
    requires = (
        "base/[^1.0.0]",
        "atk/[^2.35.1]",
        "at-spi2-core/[^2.34.0]",
        "libxml2/[^2.9.9]",
    )

    def source(self):
        tools.get(f"https://gitlab.gnome.org/GNOME/at-spi2-atk/-/archive/AT_SPI2_ATK_{self.version}/at-spi2-atk-AT_SPI2_ATK_{self.version.replace(".", "_")}.tar.bz2")

    def build(self):
        args = ["--auto-features=disabled", "--wrap-mode=nofallback"]
        meson = Meson(self)
        meson.configure(source_folder="at-spi2-atk-AT_SPI2_ATK_" + self.version.replace(".", "_"), args=args, pkg_config_paths=os.environ["PKG_CONFIG_PATH"].split(":"))
        meson.install()

    def package_info(self):
        self.env_info.GI_TYPELIB_PATH.append(os.path.join(self.package_folder, "lib", "girepository-1.0"))
