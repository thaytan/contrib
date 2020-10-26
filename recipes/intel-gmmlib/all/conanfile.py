from build import *


class IntelGmmlibRecipe(Recipe):
    description = "Intel Graphics Memory Management Library"
    license = "MIT"
    build_requires = ("cmake/[^3.18.4]",)

    def source(self):
        self.get(f"https://github.com/intel/gmmlib/archive/intel-gmmlib-{self.version}.tar.gz")
