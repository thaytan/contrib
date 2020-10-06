import os

from conans import *


class NcursesConan(ConanFile):
    description = "System V Release 4.0 curses emulation library"
    license = "MIT"
    settings = "build_type", "compiler", "arch_build", "os_build", "libc_build"
    build_requires = (
        "bootstrap-llvm/[^10.0.1]",
        "make/[^4.3]",
    )

    def source(self):
        tools.get(f"https://ftp.gnu.org/pub/gnu/ncurses/ncurses-{self.version}.tar.gz")

    def build(self):
        args = [
            "--enable-overwrite",
            "--without-debug",
            "--without-cxx-binding",
            "--enable-pc-files",
            f'--with-pkg-config-libdir={os.path.join(self.package_folder, "lib", "pkgconfig")}',
        ]
        autotools = AutoToolsBuildEnvironment(self)
        autotools.configure(f"ncurses-{self.version}", args)
        autotools.make()
        autotools.install()

    def package_info(self):
        self.env_info.TERMINFO = os.path.join(self.package_folder, "share", "terminfo")
