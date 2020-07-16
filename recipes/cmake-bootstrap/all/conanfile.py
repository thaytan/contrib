from conans import *


class CmakeBootstrapConan(ConanFile):
    name = "cmake-bootstrap"
    description = "A cross-platform open-source make system + ninja"
    license = "custom"
    settings = {"os_build": ["Linux"], "arch_build": ["x86_64", "armv8"], "libc_build": ["system"]}

    def source(self):
        tools.get(f"https://github.com/ninja-build/ninja/archive/v{self.version}.tar.gz")
        tools.get(f"https://github.com/Kitware/CMake/releases/download/v{self.version}/cmake-{self.version}.tar.gz")

    def build(self):
        with tools.chdir(f"ninja-{self.version}"):
            self.run("python configure.py --bootstrap")
        with tools.chdir(f"cmake-{self.version}"):
            self.run(f"./bootstrap --verbose --prefix={self.package_folder}")
            self.run("make install")

    def package(self):
        self.copy(os.path.join(f"ninja-{self.version}", "ninja"), "bin", keep_path=False)

    def package_info(self):
        self.env_info.CONAN_CMAKE_GENERATOR = "Ninja"
