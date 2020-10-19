import shutil
import os
from conans import *


class Openssl1Conan(ConanFile):
    description = "TLS/SSL and crypto library version 1"
    license = "BSD"
    settings = "build_type", "compiler", "arch_build", "os_build", "libc_build"
    build_requires = (
        "bootstrap-llvm/[^11.0.0]",
        "make/[^4.3]",
        "perl/[^5.30.0]",
    )
    requires = ("ca-certificates/[^20191127]",)

    def source(self):
        tools.get(f"https://github.com/openssl/openssl/archive/OpenSSL_{self.version.replace('.', '_')}.tar.gz")

    def build(self):
        args = ["shared", "no-ssl3-method"]
        if self.settings.arch_build == "x86_64":
            args += ["linux-x86_64", "enable-ec_nistp_64_gcc_128"]
        elif self.settings.arch_build == "armv8":
            args += ["linux-aarch64", "no-afalgeng"]
        with tools.chdir(f"openssl-OpenSSL_{self.version.replace('.', '_')}"):
            shutil.copy("Configure", "configure")
            autotools = AutoToolsBuildEnvironment(self)
            autotools.configure(args=args)
            autotools.make()
            autotools.install()

    def package_info(self):
        self.env_info.SSL_CERT_DIR = os.path.join(self.deps_cpp_info["ca-certificates"].rootpath, "etc", "ssl", "certs")
