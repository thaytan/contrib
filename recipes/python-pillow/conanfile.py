from build import *


class PythonPillowRecipe(Recipe):
    description = "Python Image Library"
    license = "BSD"
    settings = "build_type", "compiler",    "python"
    build_requires = (
        "cc/[^1.0.0]",
        "pkgconf/[^1.6.3]",
        "python-setuptools/[^50.3.0]",
        "zlib/[^1.2.11]",
        "libjpeg-turbo/[^2.0.4]",
    )

    def requirements(self):
        self.requires(f"python/[~{self.settings.python}]")

    def source(self):
        self.get(f"https://github.com/python-pillow/Pillow/archive/{self.version}.tar.gz")
