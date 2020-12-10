from build import *


class PythonCairoRecipe(Recipe):
    description = "Python bindings for the cairo graphics library"
    license = "LGPL"
    settings = "build_type", "compiler", "arch_build", "os_build", "libc_build", "python"
    build_requires = (
        "cc/[^1.0.0]",
        "pkgconf/[^1.6.3]",
    )
    requires = ("cairo/[^1.16.0]",)

    def requirements(self):
        self.requires(f"python/[~{self.settings.python}]")

    def source(self):
        self.get(f"https://github.com/pygobject/pycairo/releases/download/v{self.version}/pycairo-{self.version}.tar.gz")
