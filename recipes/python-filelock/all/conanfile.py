import os

from conans import *


class PythonFilelockConan(ConanFile):
    description = "A platform independent file lock"
    license = "custom"
    settings = "build_type", "compiler", "arch_build", "os_build", "libc_build"
    build_requires = ("python-setuptools/[^41.2.0]",)
    requires = (
        "base/[^1.0.0]",
        "python/[^3.7.4]",
    )

    def source(self):
        tools.get(f"https://github.com/benediktschmitt/py-filelock/archive/v{self.version}.tar.gz")

    def build(self):
        with tools.chdir(f"py-filelock-{self.version}"):
            self.run(f'python setup.py install --optimize=1 --prefix= --root="{self.package_folder}"')
