from build import *


class NodejsRecipe(Recipe):
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
        self.get(f"https://github.com/nodejs/node/archive/v{self.version}.tar.gz")

    def build(self):
        args = [
            "--without-npm",
            "--shared-openssl",
            "--shared-zlib",
        ]
        self.autotools(args)
