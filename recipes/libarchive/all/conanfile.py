from conans import *


class LibarchiveConan(ConanFile):
    description = "Multi-format archive and compression library"
    license = "BSD"
    settings = "build_type", "compiler", "arch_build", "os_build", "libc_build"
    build_requires = (
        "autotools/[^1.0.0]",
        "expat/[^2.2.7]",
        "zlib/[^1.2.11]",
        "xz/[^5.2.5]",
        "bzip2/[^1.0.8]",
    )
    requires = ("openssl1/[^1.1.1h]",)

    def source(self):
        tools.get(f"https://github.com/libarchive/libarchive/releases/download/v{self.version}/libarchive-{self.version}.tar.xz")

    def build(self):
        args = [
            "--disable-shared",
        ]
        autotools = AutoToolsBuildEnvironment(self)
        autotools.configure(f"libarchive-{self.version}", args)
        autotools.make()
        autotools.install()
