import os

from conans import *


class AtSpi2CoreConan(ConanFile):
    description = "Protocol definitions and daemon for D-Bus at-spi"
    license = "GPL2"
    settings = {"os": ["Linux"], "arch": ["x86_64", "armv8"]}
    build_requires = (
        "generators/1.0.0",
        "meson/[^0.51.2]",
    )
    requires = (
        "glib/[^2.62.0]",
        "dbus/[^1.12.16]",
    )

    def source(self):
        tools.get("https://gitlab.gnome.org/GNOME/at-spi2-core/-/archive/AT_SPI2_CORE_{0}/at-spi2-core-AT_SPI2_CORE_{0}.tar.gz".format(self.version.replace(".", "_")))

    def build(self):
        args = ["--auto-features=disabled", "--wrap-mode=nofallback"]
        meson = Meson(self)
        meson.configure(source_folder="at-spi2-core-AT_SPI2_CORE_" + self.version.replace(".", "_"), args=args, pkg_config_paths=os.environ["PKG_CONFIG_PATH"].split(":"))
        meson.install()
