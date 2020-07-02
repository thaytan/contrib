from conans import *


class FlexConan(ConanFile):
    description = "Flex, the fast lexical analyzer generator"
    license = "BSD 2-Clause"
    settings = {"os": ["Linux"], "arch": ["x86_64", "armv8"]}
    build_requires = (
        "autotools/[^1.0.0]",
        "bison/[^3.3]",
    )

    def source(self):
        tools.get(f"https://github.com/westes/flex/releases/download/v{self.version}/flex-{self.version}.tar.gz")

    def build(self):
        args = ["--disable-nls", "ac_cv_func_reallocarray=no"]
        with tools.chdir(f"{self.name}-{self.version}"):
            self.run("sh autogen.sh")
            autotools = AutoToolsBuildEnvironment(self)
            autotools.configure(args=args)
            autotools.install()
