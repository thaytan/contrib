from conans import *


class LibffiConan(ConanFile):
    description = "A portable, high level programming interface to various calling conventions"
    license = "MIT"
    settings = "build_type", "compiler", "arch_build", "os_build", "libc_build"
    build_requires = ("llvm-bootstrap/[^10.0.0]", "make/[^4.3]")

    def source(self):
        tools.get(f"https://github.com/libffi/libffi/releases/download/v{self.version}/libffi-{self.version}.tar.gz")

    def build(self):
        args = [
            "--quiet",
            "--disable-debug",
            "--disable-dependency-tracking",
            "--disable-docs",
            "--disable-shared",
        ]
        autotools = AutoToolsBuildEnvironment(self)
        autotools.configure(args=args, configure_dir=f"{self.name}-{self.version}")
        autotools.make()
        autotools.install()
