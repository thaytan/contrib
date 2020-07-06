import os

from conans import *


class PythonZippConan(ConanFile):
    description = "Pathlib-compatible object wrapper for zip files"
    license = "MIT"
    settings = {"os": ["Linux"], "arch": ["x86_64", "armv8"]}
    build_requires = ("python-setuptools/[^41.2.0]",)
    requires = (
        "base/[^1.0.0]",
        "python/[^3.7.4]",
    )

    def source(self):
        tools.get(f"https://github.com/jaraco/zipp/archive/v{self.version}.tar.gz")

    def build(self):
        with tools.chdir(f"zipp-{self.version}"):
            self.run(f'python setup.py install --optimize=1 --prefix= --root="{self.package_folder}"')
