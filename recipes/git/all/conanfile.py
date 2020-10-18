import os
from conans import *

CONFIG_MAK = """
CFLAGS={}
LDFLAGS=-ldl
"""


class GitConan(ConanFile):
    description = "The fast distributed version control system"
    license = "GPL2"
    settings = "build_type", "compiler", "arch_build", "os_build", "libc_build"
    build_requires = (
        "cc/[^1.0.0]",
        "make/[^4.3]",
        "gettext/[^0.21]",
        "zlib/[^1.2.11]",
        "curl/[^7.66.0]",
        "openssl/[^3.0.0-alpha6]",
        "expat/[^2.2.7]",
    )
    requires = ("ca-certificates/[^20191127]",)

    def source(self):
        tools.get(f"https://www.kernel.org/pub/software/scm/git/git-{self.version}.tar.xz")

    def build(self):
        args = [
            f"prefix={self.package_folder}",
        ]
        with tools.chdir(f"git-{self.version}"):
            with open("config.mak", "w") as cfg:
                cfg.write(CONFIG_MAK.format(f"-I{self.source_folder} {os.environ['CFLAGS']}"))
            autotools = AutoToolsBuildEnvironment(self)
            autotools.make(args)
            autotools.install(args)
