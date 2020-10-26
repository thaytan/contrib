import os
from conans import *


class CurlConan(ConanFile):
    description = "An URL retrieval utility and library"
    license = "MIT"
    settings = "build_type", "compiler", "arch_build", "os_build", "libc_build"
    build_requires = (
        "make/[^4.3]",
        "pkgconf/[^1.7.3]",
        "zlib/[^1.2.11]",
        "openssl/[^3.0.0-alpha6]",
    )
    requires = ("ca-certificates/[^20191127]",)

    def source(self):
        tools.get(f"https://curl.haxx.se/download/curl-{self.version}.tar.gz")

    def build(self):
        env = {
            "CFLAGS": os.environ["CFLAGS"] + "-ldl -lpthread",
        }
        args = ["--disable-shared"]
        autotools = AutoToolsBuildEnvironment(self)
        autotools.configure(f"curl-{self.version}", args, vars=env)
        autotools.make()
        autotools.install()

    def package_info(self):
        self.env_info.CURL_CA_BUNDLE = os.path.join(self.deps_cpp_info["ca-certificates"].rootpath, "etc", "ssl", "certs", "cert.pem")
