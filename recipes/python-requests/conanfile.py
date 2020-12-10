from build import *


class PythonRequestsRecipe(Recipe):
    description = "Python Requests module"
    license = "Apache 2.0"
    settings = "build_type", "compiler", "arch_build", "os_build", "libc_build", "python"
    build_requires = (
        "pkgconf/[^1.6.3]",
        "python-setuptools/[^41.2.0]",
    )

    def requirements(self):
        self.requires(f"python/[~{self.settings.python}]")

    def source(self):
        self.get(f"https://github.com/psf/requests/archive/v{self.version}.tar.gz")
