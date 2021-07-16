from build import *


class PythonImportlibMetadataRecipe(Recipe):
    description = "Read metadata from Python packages"
    license = "Apache"
    build_requires = ("python-setuptools/[>=41.2.0]",)
    requires = (
        "base/[^1.0.0]",
        "python-zipp/[^3.1.0]",
    )

    def source(self):
        self.get(f"https://gitlab.com/python-devs/importlib_metadata/-/archive/v{self.version}/importlib_metadata-v{self.version}.tar.bz2")

