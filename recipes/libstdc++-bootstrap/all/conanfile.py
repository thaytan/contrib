import os
from conans import *
import shutil


class LibstdcppBootstrapConan(ConanFile):
    name = "libstdc++-bootstrap"
    description = "GNU C++ Standard Library"
    license = "custom"
    settings = {"os": ["Linux"], "arch": ["x86_64", "armv8"]}
    build_requires = (
        "clang-bootstrap/[^10.0.0]",
        "cmake-bootstrap/[^3.17.3]",
        "linux-headers/[^5.4.50]",
    )
    requires = ("musl/[^1.2.0]",)

    def source(self):
        tools.get(f"https://sourceware.org/pub/gcc/releases/gcc-{self.version}/gcc-{self.version}.tar.xz")

    def build(self):
        env = {
            "CC": "musl-clang",
            "CXX": "musl-clang++",
        }
        args = [
            # "--build=x86_64-pc-linux-gnu",
            "--host=x86_64-pc-linux-musl",
            # "--target=x86_64-pc-linux-musl",
        ]
        with tools.chdir(os.path.join(f"gcc-{self.version}", "libstdc++-v3")), tools.environment_append(env):
            autotools = AutoToolsBuildEnvironment(self)
            autotools.configure(args=args)
            autotools.make()
            autotools.install()
