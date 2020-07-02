from conans import *


class GitConan(ConanFile):
    description = "The fast distributed version control system"
    license = "GPL2"
    settings = {"os": ["Linux"], "arch": ["x86_64", "armv8"]}
    build_requires = (
        "cc/[^1.0.0]",
        "gettext/[^0.20.1]",
    )
    requires = (
        "generators/[^1.0.0]",
        "zlib/[^1.2.11]",
        "curl/[^7.66.0]",
        "openssl/[^1.1.1b]",
    )

    def source(self):
        tools.get(f"https://www.kernel.org/pub/software/scm/git/git-{self.version}.tar.xz")

    def build(self):
        with tools.chdir(f"{self.name}-{self.version}"):
            autotools = AutoToolsBuildEnvironment(self)
            autotools.configure()
            autotools.make()
            autotools.install()
