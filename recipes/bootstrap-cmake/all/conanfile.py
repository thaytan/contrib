from conans import *


class BootstrapCMakeConan(ConanFile):
    description = "A cross-platform open-source make system + ninja"
    license = "Apache"
    settings = "build_type", "compiler", "arch_build", "os_build", "libc_build"
    build_requires = (
        "bootstrap-libc/[^1.0.0]",
        "bootstrap-openssl/[^3.0.0-alpha6]",
    )

    def source(self):
        tools.get(f"https://github.com/Kitware/CMake/releases/download/v{self.version}/cmake-{self.version}.tar.gz")

    def build(self):
        cmake = CMake(self)
        cmake.configure(source_folder=f"cmake-{self.version}")
        cmake.build()
        cmake.install()
