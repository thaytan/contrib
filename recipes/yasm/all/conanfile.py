from conans import *


class YasmConan(ConanFile):
    description = "Yasm is a complete rewrite of the NASM assembler under the “new” BSD License"
    license = "BSD"
    settings = "build_type", "compiler", "arch_build", "os_build", "libc_build"
    build_requires = (
        "cc/[^1.0.0]",
        "autotools/[^1.0.0]",
    )

    def source(self):
        tools.get(f"http://www.tortall.net/projects/yasm/releases/yasm-{self.version}.tar.gz")

    def build(self):
        autotools = AutoToolsBuildEnvironment(self)
        autotools.configure(f"yasm-{self.version}")
        autotools.install()
