from build import *


class PythonNumpyRecipe(Recipe):
    description = "conan package for Python Numpy module"
    license = "BSD"
    settings = "build_type", "compiler",    "python"
    build_requires = (
        "cc/[^1.0.0]",
        "pkgconf/[^1.6.3]",
        "python-setuptools/[>=41.2.0]",
        "cython/[^0.29.19]",
    )

    def requirements(self):
        self.requires(f"python/[^3]")

    def source(self):
        self.get(f"https://github.com/numpy/numpy/releases/download/v{self.version}/numpy-{self.version}.tar.gz")
