import glob
import os
import shutil

from conans import AutoToolsBuildEnvironment, ConanFile, tools


class PkgconfConan(ConanFile):
    description = "Package compiler and linker metadata toolkit"
    license = "custom"
    settings = {"os": ["Linux"], "arch": ["x86_64", "armv8"]}

    def build_requirements(self):
        self.build_requires("gcc/[>=7.4.0]@%s/stable" % self.user)
        self.build_requires("autoconf/[>=2.69]@%s/stable" % self.user)
        self.build_requires("automake/[>=1.16.1]@%s/stable" % self.user)
        self.build_requires("libtool/[>=2.4.6]@%s/stable" % self.user)

    def source(self):
        tools.get("https://github.com/pkgconf/pkgconf/archive/pkgconf-%s.tar.gz" % self.version)

    def build(self):
        args = ["--disable-static"]
        with tools.chdir("pkgconf-pkgconf-%s" % self.version):
            self.run("sh autogen.sh")
            autotools = AutoToolsBuildEnvironment(self)
            autotools.configure(args=args)
            autotools.make()
            autotools.install()
        os.symlink("pkgconf", os.path.join(self.package_folder, "bin", "pkg-config"))

    def package_info(self):
        self.env_info.PKG_CONFIG = os.path.join(self.package_folder, "bin", "pkgconf")
        self.env_info.ACLOCAL_PATH.append(os.path.join(self.package_folder, "share", "aclocal"))
        # Support system pkgconfig files
        if self.settings.os == "Linux":
            self.env_info.PKG_CONFIG_SYSTEM_PATH.append("/usr/share/pkgconfig")
            if self.settings.arch == "x86_64":
                self.env_info.PKG_CONFIG_SYSTEM_PATH.append("/usr/lib/x86_64-linux-gnu/pkgconfig")
            if self.settings.arch == "armv8":
                self.env_info.PKG_CONFIG_SYSTEM_PATH.append("/usr/lib/aarch64-linux-gnu/pkgconfig")
