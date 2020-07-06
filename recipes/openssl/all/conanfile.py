import os
import platform
import shutil

from conans import *


class OpensslConan(ConanFile):
    name = "openssl"
    description = "TLS/SSL and crypto library"
    license = "custom"
    settings = {"os_build": ["Linux"], "arch_build": ["x86_64", "armv8"]}
    build_requires = ("gcc/7.4.0",)

    def source(self):
        tools.get(f"https://github.com/openssl/openssl/archive/OpenSSL_{self.version}.tar.gz".replace(".", "_"))

    def build(self):
        args = ["shared", "no-ssl3-method"]
        if self.settings.arch_build == "x86_64":
            args += ["linux-x86_64", "enable-ec_nistp_64_gcc_128"]
        elif self.settings.arch_build == "armv8":
            args += ["linux-aarch64", "no-afalgeng"]
        with tools.chdir("openssl-OpenSSL_" + self.version.replace(".", "_")):
            shutil.copy("Configure", "configure")
            autotools = AutoToolsBuildEnvironment(self)
            autotools.configure(args=args)
            autotools.make()
            autotools.install()
