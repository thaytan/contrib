import os

from conans import *


class NcursesBootstrapConan(ConanFile):
    name = "ncurses-bootstrap"
    description = "System V Release 4.0 curses emulation library"
    license = "Zlib"
    settings = {"os_build": ["Linux"], "arch_build": ["x86_64", "armv8"]}

    def source(self):
        tools.get(f"https://ftp.gnu.org/pub/gnu/ncurses/ncurses-{self.version}.tar.gz")

    def build(self):
        args = [
            "--enable-overwrite",
            "--with-shared",
            "--with-cxx-shared",
            "--with-cxx-binding",
            "--enable-pc-files",
            "--with-pkg-config-libdir=" + os.path.join(self.package_folder, "lib", "pkgconfig"),
        ]
        autotools = AutoToolsBuildEnvironment(self)
        autotools.configure(args=args, configure_dir=f"ncurses-{self.version}")
        autotools.make()
        autotools.install()

    def package_info(self):
        self.env_info.TERMINFO = os.path.join(self.package_folder, "share", "terminfo")
