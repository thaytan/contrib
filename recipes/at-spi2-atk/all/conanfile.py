import os

from conans import ConanFile, Meson, tools


class AtSpi2AtkConan(ConanFile):
    description = "A GTK+ module that bridges ATK to D-Bus at-spi"
    license = "LGPL"
    settings = {"os": ["Linux"], "arch": ["x86_64", "armv8"]}

    def build_requirements(self):
        self.build_requires("generators/1.0.0")
        self.build_requires("meson/[^0.51.2]")

    def requirements(self):
        self.requires("atk/[^2.35.1]")
        self.requires("at-spi2-core/[^2.34.0]")
        self.requires("libxml2/[^2.9.9]")

    def source(self):
        tools.get("https://gitlab.gnome.org/GNOME/at-spi2-atk/-/archive/AT_SPI2_ATK_{0}/at-spi2-atk-AT_SPI2_ATK_{0}.tar.bz2".format(self.version.replace(".", "_")))

    def build(self):
        args = ["--auto-features=disabled", "--wrap-mode=nofallback"]
        meson = Meson(self)
        meson.configure(source_folder="at-spi2-atk-AT_SPI2_ATK_" + self.version.replace(".", "_"), args=args, pkg_config_paths=os.environ["PKG_CONFIG_PATH"].split(":"))
        meson.install()

    def package_info(self):
        self.env_info.GI_TYPELIB_PATH.append(os.path.join(self.package_folder, "lib", "girepository-1.0"))
