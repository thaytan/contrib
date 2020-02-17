import os
import platform
import shutil

from conans import AutoToolsBuildEnvironment, ConanFile, tools


class OpensslConan(ConanFile):
    name = "openssl"
    version = tools.get_env("GIT_TAG", "1.1.1b")
    description = "TLS/SSL and crypto library"
    url = "https://gitlab.com/aivero/public/conan/conan-" + name
    license = "custom"
    settings = "os", "compiler", "build_type", "arch"

    def build_requirements(self):
        self.build_requires("generators/1.0.0@%s/stable" % self.user)
        self.build_requires("gcc/7.4.0@%s/stable" % self.user)

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
