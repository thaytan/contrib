import os
from conans import *


class ElfutilsConan(ConanFile):
    description = "Utilities and DSOs to handle ELF files and DWARF data"
    license = "LGPL3"
    settings = "build_type", "compiler", "arch_build", "os_build", "libc_build"
    exports = ("elfutils-clang.patch",)
    build_requires = (
        "cc/[^1.0.0]",
        "autotools/[^1.0.0]",
        "zlib/[^1.2.11]",
        "libarchive/[^3.4.3]",
    )

    def source(self):
        tools.get(f"https://sourceware.org/elfutils/ftp/{self.version}/elfutils-{self.version}.tar.bz2")
        tools.patch(f"elfutils-{self.version}", "elfutils-clang.patch")

    def build(self):
        args = [
            "--disable-shared",
            "--disable-debuginfod",
        ]
        os.environ["CFLAGS"] += " -Wno-error"
        os.environ["CXXFLAGS"] += " -Wno-error"
        self.run("autoreconf -ifv", cwd=f"elfutils-{self.version}")
        autotools = AutoToolsBuildEnvironment(self)
        autotools.configure(f"elfutils-{self.version}", args)
        autotools.make()
        autotools.install()
