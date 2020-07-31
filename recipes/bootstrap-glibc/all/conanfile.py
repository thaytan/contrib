import pathlib
import os
from conans import *


class BootstrapGlibcConan(ConanFile):
    name = "bootstrap-glibc"
    description = "glibc bootstrap headers files"
    license = "GPL"
    settings = {"os_build": ["Linux"], "arch_build": ["x86_64", "armv8"], "libc_build": ["system"]}
    requires = (
        ("generators/[^1.0.0]", "private"),
        "linux-headers-bootstrap/[^5.4.50]",
    )

    def source(self):
        tools.get(f"https://ftp.gnu.org/gnu/glibc/glibc-{self.version}.tar.xz")

    def build(self):
        autotools = AutoToolsBuildEnvironment(self)
        autotools.configure(configure_dir=f"glibc-{self.version}")
        autotools.make(target="install-headers")

        # install-headers does not create include/gnu/stubs.h file
        pathlib.Path(os.path.join(self.package_folder, "include", "gnu", "stubs.h")).touch()
