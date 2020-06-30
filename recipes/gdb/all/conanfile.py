import os

from conans import *


class GdbConan(ConanFile):
    description = "The GNU Debugger"
    license = "GPL3"
    settings = {"os": ["Linux"], "arch": ["x86_64", "armv8"]}
    build_requires = (
        "generators/1.0.0",
        "gcc/[^7.4.0]",
        "texinfo/[^6.6]",
    )
    requires = (
        "python/[^3.7.4]",
        "ncurses/[^6.1]",
        "readline/[^8.0]",
    )

    def source(self):
        tools.get("https://ftp.gnu.org/gnu/gdb/gdb-%s.tar.gz" % self.version)

    def build(self):
        args = ["--enable-tui=yes", "--with-system-readline"]
        with tools.chdir("%s-%s" % (self.name, self.version)):
            autotools = AutoToolsBuildEnvironment(self)
            autotools.configure(args=args)
            autotools.make()
            autotools.install()

    def package_info(self):
        self.env_info.PYTHONPATH.append(os.path.join(self.package_folder, "share", "gdb", "python"))
