from conans import *


class GitConan(ConanFile):
    description = "The fast distributed version control system"
    license = "GPL2"
    settings = {"os": ["Linux"], "arch": ["x86_64", "armv8"]}
    build_requires = (
        "generators/1.0.0",
        "gcc/[^7.4.0]",
        "gettext/[^0.20.1]",
    )
    requires = (
        "zlib/[^1.2.11]",
        "curl/[^7.66.0]",
        "openssl/[^1.1.1b]",
    )

    def source(self):
        tools.get("https://www.kernel.org/pub/software/scm/git/git-%s.tar.xz" % self.version)

    def build(self):
        with tools.chdir("%s-%s" % (self.name, self.version)):
            autotools = AutoToolsBuildEnvironment(self)
            autotools.configure()
            autotools.make()
            autotools.install()
