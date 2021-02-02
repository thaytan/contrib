from build import *


class PythonVirtualenvRecipe(Recipe):
    description = "Virtual Python Environment builder"
    license = "MIT"
    settings = "build_type", "compiler", "arch_build", "os_build", "libc_build", "python"
    requires = (
        "python-setuptools/[^41.2.0]",
        "python-appdirs/[^1.4.4]",
        "python-distlib/[^0.3.0]",
        "python-filelock/[^3.0.12]",
        "python-six/[^1.15.0]",
        "python-importlib-metadata/[^1.6.0]",
    )

    def requirements(self):
        self.requires(f"python/[~{self.settings.python}]")

    def source(self):
        self.get(f"https://github.com/pypa/virtualenv/archive/{self.version}.tar.gz")
