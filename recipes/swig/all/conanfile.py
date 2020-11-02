from build import *


class SwigRecipe(Recipe):
    description = "Generate scripting interfaces to C/C++ code"
    license = "custom"
    settings = "build_type", "compiler", "arch_build", "os_build", "libc_build", "python"
    build_requires = (
        "cc/[^1.0.0]",
        "autotools/[^1.0.0]",
        "perl/[^5.30.0]",
    )

    def build_requirements(self):
        self.build_requires(f"python/[~{self.settings.python}]")

    def source(self):
        self.get(f"https://downloads.sourceforge.net/swig/swig-{self.version}.tar.gz")

    def build(self):
        os.environ["PATH"] += os.path.join(self.package_folder, "bin")
        self.autotools(args)
