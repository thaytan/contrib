from build import *


class SwigRecipe(PythonRecipe):
    description = "Generate scripting interfaces to C/C++ code"
    license = "custom"
    build_requires = (
        "cc/[^1.0.0]",
        "autotools/[^1.0.0]",
        "perl/[^5.30.0]",
    )

    def build_requirements(self):
        self.build_requires(f"python/[^3.6]")

    def source(self):
        self.get(f"https://downloads.sourceforge.net/swig/swig-{self.version}.tar.gz")

    def build(self):
        os.environ["PATH"] += os.path.join(self.package_folder, "bin")
        self.autotools()
