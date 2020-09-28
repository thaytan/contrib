import pathlib
import os
from conans import *


class BootstrapGlibcHeadersConan(ConanFile):
    description = "glibc bootstrap headers"
    license = "GPL"
    settings = "build_type", "compiler", "arch_build", "os_build", "libc_build"
    requires = ("bootstrap-linux-headers/[^5.4.50]",)
    no_dev_pkg = True

    def source(self):
        tools.get(f"https://ftp.gnu.org/gnu/glibc/glibc-{self.version}.tar.xz")

    def build(self):
        autotools = AutoToolsBuildEnvironment(self)
        autotools.configure(configure_dir=f"glibc-{self.version}")
        autotools.make(target="install-headers")

        # install-headers does not create include/gnu/stubs.h
        pathlib.Path(os.path.join(self.package_folder, "include", "gnu", "stubs.h")).touch()
