from build import *


class ItstoolRecipe(Recipe):
    description = "XML to PO and back again"
    license = "GPL3"
    settings = "build_type", "compiler", "arch_build", "os_build", "libc_build", "python"
    build_requires = ("autotools/[^1.0.0]",)
    requires = ("libxml2/[^2.9.10]",)

    def requirements(self):
        self.requires(f"python/[~{self.settings.python}]")

    def source(self):
        self.get(f"https://github.com/itstool/itstool/archive/{self.version}.tar.gz")
