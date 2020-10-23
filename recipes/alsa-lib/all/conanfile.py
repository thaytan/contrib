from conans import *


class AlsaLibConan(ConanFile):
    description = "An alternative implementation of Linux sound support"
    license = "LGPL2.1"
    settings = "build_type", "compiler", "arch_build", "os_build", "libc_build"
    build_requires = (
        "cc/[^1.0.0]",
        "autotools/[^1.0.0]",
    )

    def source(self):
        tools.get(f"https://www.alsa-project.org/files/pub/lib/alsa-lib-{self.version}.tar.bz2")

    def build(self):
        args = [
            "--disable-static",
        ]
        autotools = AutoToolsBuildEnvironment(self)
        autotools.configure(f"alsa-lib-{self.version}", args)
        autotools.make()
        autotools.install()
