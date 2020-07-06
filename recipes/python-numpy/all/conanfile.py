import os

from conans import *


class PythonNumpyConan(ConanFile):
    name = "python-numpy"
    description = "conan package for Python Numpy module"
    license = "BSD"
    settings = {"os_build": ["Linux"], "arch_build": ["x86_64", "armv8"]}
    build_requires = (
        "cc/[^1.0.0]",
        "pkgconf/[^1.6.3]",
        "python-setuptools/[^41.2.0]",
        "cython/[^0.29.19]",
    )
    requires = (
        "base/[^1.0.0]",
        "python/[^3.7.4]",
    )

    def source(self):
        tools.get(f"https://github.com/numpy/numpy/releases/download/v{self.version}/numpy-{self.version}.tar.gz")

    def build(self):
        with tools.chdir(f"numpy-{self.version}"):
            self.run('python setup.py install --optimize=1 --prefix= --root="%s"' % self.package_folder)

