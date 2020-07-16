import os

from conans import *


class NcursesConan(ConanFile):
    name = "ncurses"
    description = "System V Release 4.0 curses emulation library"
    license = "MIT"
    settings = {"os_build": ["Linux"], "arch_build": ["x86_64", "armv8"], "libc_build": ["system"]}
    build_requires = ("llvm-bootstrap/[^10.0.0]",)
    requires = ("generators/[^1.0.0]",)

    def source(self):
        tools.get(f"https://ftp.gnu.org/pub/gnu/ncurses/ncurses-{self.version}.tar.gz")

    def build(self):
        args = [
            "--enable-overwrite",
            "--with-shared",
            "--without-normal",
            "--without-debug",
            "--without-cxx-binding",
            "--enable-pc-files",
            "--with-pkg-config-libdir=" + os.path.join(self.package_folder, "lib", "pkgconfig"),
        ]
        autotools = AutoToolsBuildEnvironment(self)
        autotools.configure(args=args, configure_dir=f"{self.name}-{self.version}")
        autotools.make()
        autotools.install()

    def package_info(self):
        self.env_info.TERMINFO = os.path.join(self.package_folder, "share", "terminfo")
