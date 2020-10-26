import os
from conans import *


class PkgconfConan(ConanFile):
    description = "Package compiler and linker metadata toolkit"
    license = "custom"
    settings = "build_type", "compiler", "arch_build", "os_build", "libc_build"
    build_requires = (
        "automake/[^1.16.1]",
        "libtool/[^2.4.6]",
    )

    def source(self):
        tools.get(f"https://github.com/pkgconf/pkgconf/archive/pkgconf-{self.version}.tar.gz")

    def build(self):
        args = ["--disable-shared"]
        self.run("sh autogen.sh", cwd=f"pkgconf-pkgconf-{self.version}")
        autotools = AutoToolsBuildEnvironment(self)
        autotools.configure(f"pkgconf-pkgconf-{self.version}", args)
        autotools.make()
        autotools.install()
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
