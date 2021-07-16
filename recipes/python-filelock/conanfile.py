from build import *


class PythonFilelockRecipe(Recipe):
    description = "A platform independent file lock"
    license = "custom"
    settings = "build_type", "compiler", "python"
    build_requires = ("python-setuptools/[>=41.2.0]", )

    def requirements(self):
        self.requires(f"python/[^3]")

    def source(self):
        self.get(
            f"https://github.com/benediktschmitt/py-filelock/archive/v{self.version}.tar.gz"
        )
