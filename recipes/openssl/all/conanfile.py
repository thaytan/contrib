import shutil
from conans import *


class OpensslConan(ConanFile):
    description = "TLS/SSL and crypto library"
    license = "BSD"
    settings = "build_type", "compiler", "arch_build", "os_build", "libc_build"
    build_requires = (
        "bootstrap-llvm/[^10.0.1]",
        "make/[^4.3]",
        "perl/[^5.30.0]",
    )

    def source(self):
        tools.get(f"https://github.com/openssl/openssl/archive/openssl-{self.version}.tar.gz")

    def build(self):
        args = ["no-shared", "no-ssl3-method"]
        if self.settings.arch_build == "x86_64":
            args += ["linux-x86_64", "enable-ec_nistp_64_gcc_128"]
        elif self.settings.arch_build == "armv8":
            args += ["linux-aarch64", "no-afalgeng"]
        with tools.chdir(f"openssl-openssl-{self.version}"):
            shutil.copy("Configure", "configure")
            autotools = AutoToolsBuildEnvironment(self)
            autotools.configure(args=args)
            autotools.make()
            autotools.install()
