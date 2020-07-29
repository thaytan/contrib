import os
from conans import *


class CmakeBootstrapConan(ConanFile):
    name = "cmake-bootstrap"
    ninja_version = "1.10.0"
    description = "A cross-platform open-source make system + ninja"
    license = "custom", "Apache"
    settings = {"os_build": ["Linux", "Windows"], "arch_build": ["x86_64", "armv8"], "libc_build": ["system"]}

    def source(self):
        tools.get(f"https://github.com/ninja-build/ninja/archive/v{self.ninja_version}.tar.gz")
        tools.get(f"https://github.com/Kitware/CMake/releases/download/v{self.version}/cmake-{self.version}.tar.gz")

    def build(self):
        self.run("python configure.py --bootstrap", cwd=os.path.join(self.build_folder, f"ninja-{self.ninja_version}"))

        cmake = CMake(self)
        cmake.definitions["CMAKE_USE_OPENSSL"] = False
        cmake.configure(source_folder=f"cmake-{self.version}")
        cmake.build()
        cmake.install()

    def package(self):
        self.copy(os.path.join(f"ninja-{self.ninja_version}", "ninja"), "bin", keep_path=False)

    def package_info(self):
        self.env_info.CONAN_CMAKE_GENERATOR = "Ninja"
