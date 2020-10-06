import os

from conans import *


class AutomakeConan(ConanFile):
    description = "A GNU tool for automatically creating Makefiles"
    license = "GPL"
    settings = "build_type", "compiler", "arch_build", "os_build", "libc_build"
    exports = "automake-include-fix.patch"
    build_requires = ("bootstrap-llvm/[^10.0.1]",)
    requires = ("autoconf/[^2.69]",)

    def source(self):
        tools.get(f"https://ftp.gnu.org/gnu/automake/automake-{self.version}.tar.gz")
        tools.patch(patch_file="automake-include-fix.patch", base_path=f"{self.name}-{self.version}")

    def build(self):
        autotools = AutoToolsBuildEnvironment(self)
        autotools.configure(f"automake-{self.version}")
        autotools.make()
        autotools.install()

    def package_info(self):
        self.env_info.AUTOMAKE = os.path.join(self.package_folder, "bin", "automake")
        self.env_info.AUTOMAKE_DIR = os.path.join(self.package_folder, "share")
        self.env_info.AUTOMAKE_LIBDIR = os.path.join(self.package_folder, "share", "automake-1.16")
        self.env_info.ACLOCAL = os.path.join(self.package_folder, "bin", "aclocal")
        self.env_info.ACLOCAL_DIR = os.path.join(self.package_folder, "share")
        self.env_info.ACLOCAL_PATH.append(os.path.join(self.package_folder, "share", "aclocal-1.16"))
        self.env_info.PERL5LIB.append(os.path.join(self.package_folder, "share", "automake-1.16"))
