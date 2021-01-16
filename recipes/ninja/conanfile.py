from build import *


class NinjaRecipe(Recipe):
    description = "Small build system with a focus on speed"
    license = "Apache"
    options = {"bootstrap": [True, False]}
    default_options = ("bootstrap=False",)
    build_requires = ("cmake-bootstrap/[^3.18.4]",)

    def build_requirements(self):
        if not self.options.bootstrap:
            self.build_requires("cc/[^1.0.0]")
            self.build_requires("make/[^4.3]")

    def source(self):
        self.get(f"https://github.com/ninja-build/ninja/archive/v{self.version}.tar.gz")

    def package_info(self):
        self.env_info.CONAN_CMAKE_GENERATOR = "Ninja"
