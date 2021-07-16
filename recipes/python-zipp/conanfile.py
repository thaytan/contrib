from build import *


class PythonZippRecipe(Recipe):
    description = "Pathlib-compatible object wrapper for zip files"
    license = "MIT"
    settings = "build_type", "compiler",    "python"
    build_requires = ("python-setuptools/[>=41.2.0]",)

    def requirements(self):
        self.requires(f"python/[~{self.settings.python}]")

    def source(self):
        self.get(f"https://github.com/jaraco/zipp/archive/v{self.version}.tar.gz")
