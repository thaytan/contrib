from build import *


class PythonZippRecipe(PythonRecipe):
    description = "Pathlib-compatible object wrapper for zip files"
    license = "MIT"

    def source(self):
        self.get(f"https://github.com/jaraco/zipp/archive/v{self.version}.tar.gz")
