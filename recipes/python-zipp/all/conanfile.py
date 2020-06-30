import os

from conans import *


class PythonZippConan(ConanFile):
    description = "Pathlib-compatible object wrapper for zip files"
    license = "MIT"
    settings = {"os": ["Linux"], "arch": ["x86_64", "armv8"]}
    build_requires = (
        "generators/1.0.0",
        "python-setuptools/[^41.2.0]",
    )
    requires = ("python/[^3.7.4]",)

    def source(self):
        tools.get("https://github.com/jaraco/zipp/archive/v{0}.tar.gz".format(self.version))

    def build(self):
        with tools.chdir("zipp-{}".format(self.version)):
            self.run('python setup.py install --optimize=1 --prefix= --root="{}"'.format(self.package_folder))
