from conans import ConanFile, tools, AutoToolsBuildEnvironment
import os
import platform
import shutil

class OpensslConan(ConanFile):
    name = "openssl"
    version = "1.1.1b"
    description = "TLS/SSL and crypto library"
    url = "https://gitlab.com/aivero/public/conan/conan-" + name
    license = "https://raw.githubusercontent.com/openssl/openssl/master/LICENSE"
    settings = "os", "compiler", "build_type", "arch"
    generators = "env"

    def requirements(self):
        self.requires("env-generator/0.1@%s/%s" % (self.user, self.channel))

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
            autotools.install()

    def package(self):
        if self.settings.build_type == "Debug":
            self.copy("*.c", "src")
            self.copy("*.h", "src")

    def package_info(self):
        self.cpp_info.libs = ["ssl", "crypto"]
        self.cpp_info.srcdirs.append("src")
