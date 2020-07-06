import os
import platform
import shutil

from conans import *


class OpensslBoostrapConan(ConanFile):
    name = "openssl-bootstrap"
    description = "TLS/SSL and crypto library"
    license = "custom"
    settings = {"os": ["Linux"], "arch": ["x86_64", "armv8"]}

    def source(self):
        tools.get(f"https://www.openssl.org/source/openssl-{self.version}.tar.gz")

    def build(self):
        args = ["shared", "no-ssl3-method"]
        if self.settings.arch == "x86_64":
            args += ["linux-x86_64", "enable-ec_nistp_64_gcc_128"]
        elif self.settings.arch == "armv8":
            args += ["linux-aarch64", "no-afalgeng"]
        with tools.chdir(f"openssl-{self.version}"):
            shutil.copy("Configure", "configure")
            autotools = AutoToolsBuildEnvironment(self)
            autotools.configure(args=args)
            autotools.make()
            autotools.install()
