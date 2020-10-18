import os

from conans import *


class PythonPipConan(ConanFile):
    description = "High productivity build system"
    license = "MIT"
    settings = "build_type", "compiler", "arch_build", "os_build", "libc_build"

    def source(self):
        tools.get(f"https://github.com/pypa/pip/archive/{self.version}.tar.gz")

    build_requires = ("python-setuptools/[^41.2.0]",)
    requires = (
        "base/[^1.0.0]",
        "python/[^3.7.4]",
    )

    def build(self):
        with tools.chdir("pip-" + self.version):
            self.run('python setup.py install --optimize=1 --prefix= --root="%s"' % self.package_folder)
