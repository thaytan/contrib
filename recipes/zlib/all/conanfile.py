from conans import *


class ZlibConan(ConanFile):
    description = "A Massively Spiffy Yet Delicately Unobtrusive Compression Library (Also Free, Not to Mention Unencumbered by Patents)"
    license = "Zlib"
    settings = "build_type", "compiler", "arch_build", "os_build", "libc_build"
    build_requires = (
        "bootstrap-llvm/[^10.0.1]",
        "make/[^4.3]",
    )

    def source(self):
        tools.get(f"https://github.com/madler/zlib/archive/v{self.version}.tar.gz")

    def build(self):
        args = [
            "--static",
        ]
        autotools = AutoToolsBuildEnvironment(self)
        autotools.configure(f"zlib-{self.version}", args)
        autotools.make()
        autotools.install()
