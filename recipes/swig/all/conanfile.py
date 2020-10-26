import os
from conans import *


class SwigConan(ConanFile):
    description = "Generate scripting interfaces to C/C++ code"
    license = "custom"
    settings = "build_type", "compiler", "arch_build", "os_build", "libc_build", "python"
    build_requires = (
        "autotools/[^1.0.0]",
        "perl/[^5.30.0]",
    )

    def build_requirements(self):
        self.build_requires(f"python/[~{self.settings.python}]")

    def source(self):
        tools.get(f"https://downloads.sourceforge.net/swig/swig-{self.version}.tar.gz")

    def build(self):
        env = {"PATH": tools.get_env("PATH") + os.path.pathsep + os.path.join(self.package_folder, "bin")}
        with tools.environment_append(env):
            autotools = AutoToolsBuildEnvironment(self)
            autotools.configure(f"swig-{self.version}")
            autotools.install()
