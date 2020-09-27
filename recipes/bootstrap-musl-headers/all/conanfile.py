from conans import *


class BootstrapMuslHeadersConan(ConanFile):
    description = "Lightweight implementation of C standard library"
    license = "MIT"
    settings = "build_type", "compiler", "arch_build", "os_build", "libc_build"
    requires = ("bootstrap-linux-headers/[^5.4.50]",)
    no_dev_pkg = True

    def source(self):
        tools.get(f"https://www.musl-libc.org/releases/musl-{self.version}.tar.gz")

    def build(self):
        autotools = AutoToolsBuildEnvironment(self)
        autotools.configure(configure_dir=f"musl-{self.version}")
        autotools.make(target="install-headers")
