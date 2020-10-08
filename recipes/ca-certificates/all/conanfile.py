import os
from conans import *


class CaCertificatesConan(ConanFile):
    description = "Common CA certificates PEM files from Mozilla"
    license = "MPL-2.0"
    settings = "build_type", "compiler", "arch_build", "os_build", "libc_build"

    build_requires = (
        "bootstrap-openssl/[^3.0.0-alpha6]",
        "make/[^4.3]",
        "python/[^3.8.5]",
        "clang/[^10.0.1]",
    )

    def source(self):
        tools.get(f"https://gitlab.alpinelinux.org/alpine/ca-certificates/-/archive/{self.version}/ca-certificates-{self.version}.tar.bz2")

    def build(self):
        env = {"DESTDIR": self.package_folder, "CFLAGS": os.environ["CFLAGS"] + f" -ldl -lpthread -I{self.deps_cpp_info['openssl'].rootpath}/include"}
        with tools.chdir(f"ca-certificates-{self.version}"), tools.environment_append(env):
            autotools = AutoToolsBuildEnvironment(self)
            autotools.make()
            self.run("mv NetLock_Arany_*.crt NetLock_Arany.crt")

    def package(self):
        self.copy("*.crt", dst="share/ca-certificates")
