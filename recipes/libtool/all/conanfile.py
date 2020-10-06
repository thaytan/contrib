import os

from conans import *


class LibtoolConan(ConanFile):
    description = "A generic library support script"
    license = "GPL"
    settings = "build_type", "compiler", "arch_build", "os_build", "libc_build"
    exports = "libtool-prefix-fix.patch"
    build_requires = (
        "clang/[^10.0.1]",
        "automake/[^1.16.1]",
        "help2man/[^1.47.11]",
        "texinfo/[^6.6]",
    )

    def source(self):
        tools.get(f"https://ftp.gnu.org/gnu/libtool/libtool-{self.version}.tar.gz")
        tools.patch(
            patch_file="libtool-prefix-fix.patch", base_path=f"libtool-{self.version}",
        )

    def build(self):
        args = [
            "--disable-shared",
        ]
        autotools = AutoToolsBuildEnvironment(self)
        autotools.configure(f"libtool-{self.version}", args)
        autotools.make()
        autotools.install()

    def package_info(self):
        self.env_info.LIBTOOL_PREFIX = self.package_folder
        self.env_info.LIBTOOL = os.path.join(self.package_folder, "bin", "libtool")
        self.env_info.LIBTOOLIZE = os.path.join(self.package_folder, "bin", "libtoolize")
        self.env_info.ACLOCAL_PATH.append(os.path.join(self.package_folder, "share", "aclocal"))
