import shutil
import os
from conans import *


class OpensslConan(ConanFile):
    description = "TLS/SSL and crypto library"
    license = "BSD"
    settings = "build_type", "compiler", "arch_build", "os_build", "libc_build"
    build_requires = (
        "make/[^4.3]",
        "perl/[^5.30.0]",
    )
    requires = ("ca-certificates/[^20191127]",)

    def source(self):
        tools.get(f"https://github.com/openssl/openssl/archive/openssl-{self.version}.tar.gz")

    def build(self):
        args = ["shared", "no-ssl3-method"]
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
        libs = ["crypto", "ssl"]
        for lib in libs:
            os.remove(os.path.join(self.package_folder, "lib", f"lib{lib}.a"))

    def package_info(self):
        self.env_info.SSL_CERT_DIR = os.path.join(self.deps_cpp_info["ca-certificates"].rootpath, "etc", "ssl", "certs")
