from build import *


class PythonCythonRecipe(Recipe):
    description = "Python to C compiler"
    license = "Apache"
    settings = "build_type", "compiler",    "python"
    build_requires = (
        "cc/[^1.0.0]",
        "pkgconf/[^1.6.3]",
        "python-setuptools/[^41.2.0]",
    )

    def requirements(self):
        self.requires(f"python/[~{self.settings.python}]")

    def source(self):
        self.get(f"https://github.com/cython/cython/archive/{self.version}.tar.gz")
