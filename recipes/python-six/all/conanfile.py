import os

from conans import *


class PythonSixConan(ConanFile):
    description = "Python 2 and 3 compatibility utilities"
    license = "MIT"
    settings = "build_type", "compiler", "arch_build", "os_build", "libc_build"
    build_requires = (
        "autotools/1.0.0",
        "python-setuptools/[^41.2.0]",
    )

    def source(self):
        tools.get(f"https://pypi.io/packages/source/s/six/six-{self.version}.tar.gz")

    def build(self):
        with tools.chdir(f"six-{self.version}"):
            self.run('python setup.py install --optimize=1 --prefix= --root="%s"' % self.package_folder)
