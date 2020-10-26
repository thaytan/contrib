from build import *


class PkgconfRecipe(Recipe):
    description = "Package compiler and linker metadata toolkit"
    license = "custom"
    build_requires = (
        "automake/[^1.16.1]",
        "libtool/[^2.4.6]",
    )

    def source(self):
        self.get(f"https://github.com/pkgconf/pkgconf/archive/pkgconf-{self.version}.tar.gz")

    def package(self):
        os.symlink("pkgconf", os.path.join(self.package_folder, "bin", "pkg-config"))

    def package_info(self):
        self.env_info.PKG_CONFIG = os.path.join(self.package_folder, "bin", "pkgconf")
        self.env_info.ACLOCAL_PATH.append(os.path.join(self.package_folder, "share", "aclocal"))
        # Support system pkgconfig files
        # if self.settings.os == "Linux":
        #    self.env_info.PKG_CONFIG_SYSTEM_PATH.append("/usr/share/pkgconfig")
        #    if self.settings.arch_build == "x86_64":
        #        self.env_info.PKG_CONFIG_SYSTEM_PATH.append("/usr/lib/x86_64-linux-gnu/pkgconfig")
        #    if self.settings.arch_build == "armv8":
        #        self.env_info.PKG_CONFIG_SYSTEM_PATH.append("/usr/lib/aarch64-linux-gnu/pkgconfig")
