from build import *


class PythonRequestsRecipe(Recipe):
    description = "Python Requests module"
    license = "Apache"
    build_requires = (
        "pkgconf/[^1.6.3]",
        "python-setuptools/[>=41.2.0]",
    )

    def requirements(self):
        self.requires(f"python/[^3]")

    def source(self):
        self.get(f"https://github.com/psf/requests/archive/v{self.version}.tar.gz")
