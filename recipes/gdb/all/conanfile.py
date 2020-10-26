import os
from conans import *


class GdbConan(ConanFile):
    description = "The GNU Debugger"
    license = "GPL3"
    settings = "build_type", "compiler", "arch_build", "os_build", "libc_build", "python"
    build_requires = ("texinfo/[^6.6]",)
    requires = (
        "ncurses/[^6.1]",
        "readline/[^8.0]",
    )

    def requirements(self):
        self.requires(f"python/[~{self.settings.python}]")

    def source(self):
        tools.get(f"https://ftp.gnu.org/gnu/gdb/gdb-{self.version}.tar.gz")

    def build(self):
        args = ["--enable-tui=yes", "--with-system-readline"]
        with tools.chdir(f"{self.name}-{self.version}"):
            autotools = AutoToolsBuildEnvironment(self)
            autotools.configure(args=args)
            autotools.make()
            autotools.install()

    def package_info(self):
        self.env_info.PYTHONPATH.append(os.path.join(self.package_folder, "share", "gdb", "python"))
