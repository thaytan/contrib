from conans import *


class FlexConan(ConanFile):
    description = "Flex, the fast lexical analyzer generator"
    license = "BSD"
    settings = "build_type", "compiler", "arch_build", "os_build", "libc_build"
    build_requires = (
        "autotools/[^1.0.0]",
        "bison/[^3.7.2]",
    )

    def source(self):
        tools.get(f"https://github.com/westes/flex/releases/download/v{self.version}/flex-{self.version}.tar.gz")

    def build(self):
        args = [
            "--disable-nls",
            "--disable-shared",
            "ac_cv_func_reallocarray=no",
        ]
        with tools.chdir(f"flex-{self.version}"):
            self.run("sh autogen.sh")
            autotools = AutoToolsBuildEnvironment(self)
            autotools.configure(args=args)
            autotools.install()
