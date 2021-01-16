from build import *


class CMakeRecipe(Recipe):
    description = "A cross-platform open-source make system"
    license = "custom"
    options = {}
    default_options = ()

    def requirements(self):
        if self.name == "cmake":
            self.requires("cc/[^1.0.0]")
            self.requires("ninja/[^1.10.0]")
            self.requires("pkgconf/[^1.7.3]")

    def source(self):
        self.get(f"https://github.com/Kitware/CMake/releases/download/v{self.version}/cmake-{self.version}.tar.gz")

    def build(self):
        defs = {"CMAKE_USE_OPENSSL": False}
        self.cmake(defs)
