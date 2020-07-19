from conans import *


class ZlibConan(ConanFile):
    name = "zlib"
    description = "A Massively Spiffy Yet Delicately Unobtrusive Compression Library (Also Free, Not to Mention Unencumbered by Patents)"
    license = "Zlib"
    settings = {"os_build": ["Linux"], "arch_build": ["x86_64", "armv8"], "libc_build": ["system"]}
    build_requires = ("llvm-bootstrap/[^10.0.0]",)
    requires = ("generators/[^1.0.0]",)

    def source(self):
        tools.get(f"https://github.com/madler/zlib/archive/v{self.version}.tar.gz")

    def build(self):
        args = [
            "--static",
        ]
        autotools = AutoToolsBuildEnvironment(self)
        autotools.configure(args=args, configure_dir=f"{self.name}-{self.version}")
        autotools.make()
        autotools.install()
