from conans import *


class LibffiConan(ConanFile):
    name = "libffi"
    description = "A portable, high level programming interface to various calling conventions"
    license = "MIT"
    settings = {"os_build": ["Linux"], "arch_build": ["x86_64", "armv8"], "libc_build": ["system"]}
    build_requires = ("llvm-bootstrap-dev/[^10.0.0]",)
    requires = (("generators/[^1.0.0]", "private"),)

    def source(self):
        tools.get(f"https://github.com/libffi/libffi/archive/v{self.version}.tar.gz")

    def build(self):
        args = [
            "--quiet",
            "--disable-debug",
            "--disable-dependency-tracking",
            "--disable-docs",
            "--disable-shared",
        ]
        with tools.chdir(f"{self.name}-{self.version}"):
            self.run("sh autogen.sh")
            autotools = AutoToolsBuildEnvironment(self)
            autotools.configure(args=args)
            autotools.make()
            autotools.install()
