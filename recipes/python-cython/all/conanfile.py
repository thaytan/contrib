import os

from conans import *


class PythonCythonConan(ConanFile):
    description = "Python to C compiler"
    license = "Apache"
    settings = {"os": ["Linux"], "arch": ["x86_64", "armv8"]}
    build_requires = (
        "cc/[^1.0.0]",
        "pkgconf/[^1.6.3]",
        "python-setuptools/[^41.2.0]",
    )
    requires = (
        "generators/[^1.0.0]",
        "python/[^3.7.4]",
    )

    def source(self):
        tools.get(f"https://github.com/cython/cython/archive/{self.version}.tar.gz")

    def build(self):
        with tools.chdir(f"cython-{self.version}"):
            self.run('python setup.py install --optimize=1 --prefix= --root="%s"' % self.package_folder)

