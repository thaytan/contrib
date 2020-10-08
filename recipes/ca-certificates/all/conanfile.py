import os
import glob
import pathlib
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
        env = {"DESTDIR": self.package_folder, "CFLAGS": os.environ["CFLAGS"] + f" -ldl -lpthread -I{self.deps_cpp_info['bootstrap-openssl'].rootpath}/include"}
        ca_cert = open("ca-certificates.crt", "w")
        with tools.chdir(f"ca-certificates-{self.version}"), tools.environment_append(env):
            autotools = AutoToolsBuildEnvironment(self)
            autotools.make()
            # NetLock Arany contains invalid utf-8 characters, which is not supported in Python 3.6
            self.run("mv NetLock_Arany_*.crt NetLock_Arany.crt")
            for cert in glob.glob("*.crt"):
                ca_cert.write(pathlib.Path(cert).read_text())
        ca_cert.close()
        os.symlink("ca-certificates.crt", "cert.pem")

    def package(self):
        self.copy("*.crt", dst="share/ca-certificates", keep_path=False)
        self.copy("*ca-certificates.crt", dst="etc/ssl/certs")
        self.copy("*cert.pem", dst="etc/ssl/certs", symlinks=True)
