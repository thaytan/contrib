from build import *


class PythonDistlibRecipe(Recipe):
    description = "Low-level components of distutils2/packaging"
    license = "PSF"

    def requirements(self):
        self.requires(f"python/[^3]")

    def source(self):
        self.get(
            f"https://files.pythonhosted.org/packages/source/d/distlib/distlib-{self.version}.zip"
        )
