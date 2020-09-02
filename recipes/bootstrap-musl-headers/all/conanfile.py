import os

from conans import *


class BootstrapMuslHeadersConan(ConanFile):
    name = "bootstrap-musl-headers"
    description = "Lightweight implementation of C standard library"
    license = "MIT"
    settings = "build_type", "compiler", "arch_build", "os_build"
    requires = (
        ("generators/[^1.0.0]", "private"),
        "bootstrap-linux-headers/[^5.4.50]",
    )

    def source(self):
        tools.get(f"https://www.musl-libc.org/releases/musl-{self.version}.tar.gz")

    def build(self):
        autotools = AutoToolsBuildEnvironment(self)
        autotools.configure(configure_dir=f"musl-{self.version}")
        autotools.make(target="install-headers")

    def package_info(self):
        self.env_info.CPATH.append(os.path.join(self.package_folder, "include"))
