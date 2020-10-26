import os
from conans import *


class M4Conan(ConanFile):
    description = "The GNU macro processor"
    license = "GPL3"
    settings = "build_type", "compiler", "arch_build", "os_build", "libc_build"
    build_requires = ("make/[^4.3]",)

    def source(self):
        tools.get(f"https://ftp.gnu.org/gnu/m4/m4-{self.version}.tar.gz")

    def build(self):
        autotools = AutoToolsBuildEnvironment(self)
        autotools.configure(f"m4-{self.version}")
        autotools.make()
        autotools.install()

    def package_info(self):
        self.env_info.M4 = os.path.join(self.package_folder, "bin", "m4")
