import os
from conans import *


class TclConan(ConanFile):
    description = "The Tcl scripting language"
    license = "custom"
    settings = "build_type", "compiler", "arch_build", "os_build", "libc_build"
    build_requires = (
        "make/[^4.3]",
        "zlib/[^1.2.11]",
    )

    def source(self):
        tools.get(f"https://downloads.sourceforge.net/sourceforge/tcl/tcl{self.version}-src.tar.gz")

    def build(self):
        env = {"CFLAGS": f" -lm {os.environ['CFLAGS']}"}
        args = [
            "--disable-shared",
            "--enable-threads",
            "--enable-64bit",
        ]
        autotools = AutoToolsBuildEnvironment(self)
        autotools.configure(os.path.join(f"tcl{self.version}", "unix"), args, vars=env)
        autotools.install()
