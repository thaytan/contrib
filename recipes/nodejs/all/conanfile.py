from conans import *


class NodejsConan(ConanFile):
    description = "Evented I/O for V8 javascript"
    license = "MIT"
    settings = "build_type", "compiler", "arch_build", "os_build", "libc_build", "python"
    build_requires = ("autotools/[^1.0.0]",)
    requires = (
        "openssl/[^1.1.1b]",
        "zlib/[^1.2.11]",
    )

    def build_requirements(self):
        self.build_requires(f"python/[~{self.settings.python}]")

    def source(self):
        tools.get(f"https://github.com/nodejs/node/archive/v{self.version}.tar.gz")

    def build(self):
        args = ["--without-npm", "--shared-openssl", "--shared-zlib"]
        with tools.chdir(f"node-{self.version}"):
            autotools = AutoToolsBuildEnvironment(self)
            autotools.configure(args=args)
            autotools.install()
