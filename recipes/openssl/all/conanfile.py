import os
import platform
import shutil

from conans import *


class OpensslConan(ConanFile):
    description = "TLS/SSL and crypto library"
    license = "custom"
    settings = {"os": ["Linux"], "arch": ["x86_64", "armv8"]}

    def build_requirements(self):
        self.build_requires("generators/1.0.0")
        self.build_requires("gcc/7.4.0")

    def source(self):
        tools.get("https://github.com/openssl/openssl/archive/OpenSSL_%s.tar.gz" % self.version.replace(".", "_"))

    def build(self):
        args = ["shared", "no-ssl3-method"]
        if self.settings.arch == "x86_64":
            args += ["linux-x86_64", "enable-ec_nistp_64_gcc_128"]
        elif self.settings.arch == "armv8":
            args += ["linux-aarch64", "no-afalgeng"]
        with tools.chdir("openssl-OpenSSL_" + self.version.replace(".", "_")):
            shutil.copy("Configure", "configure")
            autotools = AutoToolsBuildEnvironment(self)
            autotools.configure(args=args)
            autotools.make()
            autotools.install()
