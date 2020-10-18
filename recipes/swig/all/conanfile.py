import os
from conans import *


class SwigConan(ConanFile):
    description = "Generate scripting interfaces to C/C++ code"
    license = "custom"
    settings = "build_type", "compiler", "arch_build", "os_build", "libc_build"
    build_requires = (
        "cc/[^1.0.0]",
        "autotools/[^1.0.0]",
        "python/[^3.8.5]",
    )

    def source(self):
        tools.get(f"https://downloads.sourceforge.net/swig/swig-{self.version}.tar.gz")

    def build(self):
        env = {"PATH": tools.get_env("PATH") + os.path.pathsep + os.path.join(self.package_folder, "bin")}
        with tools.environment_append(env):
            autotools = AutoToolsBuildEnvironment(self)
            autotools.configure(f"swig-{self.version}")
            autotools.install()
