from conans import *


class LibgpgErrorConan(ConanFile):
    description = "Support library for libgcrypt"
    license = "LGPL"
    settings = "build_type", "compiler", "arch_build", "os_build", "libc_build"
    build_requires = ("autotools/[^1.0.0]",)

    def source(self):
        tools.get(f"https://www.gnupg.org/ftp/gcrypt/libgpg-error/libgpg-error-{self.version}.tar.bz2")

    def build(self):
        args = [
            "--disable-static",
        ]
        autotools = AutoToolsBuildEnvironment(self)
        autotools.configure(f"libgpg-error-{self.version}", args)
        autotools.make()
        autotools.install()
