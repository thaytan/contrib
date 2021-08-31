from build import *


class PythonImportlibMetadataRecipe(PythonRecipe):
    description = "Read metadata from Python packages"
    license = "Apache"
    requires = ("python-zipp/[^3.1.0]", )

    def source(self):
        self.get(
            f"https://gitlab.com/python-devs/importlib_metadata/-/archive/v{self.version}/importlib_metadata-v{self.version}.tar.bz2"
        )
