import os

from conans import *


class PythonRequestsConan(ConanFile):
    description = "Python Requests module"
    license = "Apache 2.0"
    settings = {"os": ["Linux"], "arch": ["x86_64", "armv8"]}
    build_requires = (
        "cc/[^1.0.0]",
        "pkgconf/[^1.6.3]",
        "python-setuptools/[^41.2.0]",
    )
    requires = (
        "base/[^1.0.0]",
        "python/[^3.7.4]",
    )

    def source(self):
        tools.get(f"https://github.com/psf/requests/archive/v{self.version}.tar.gz")

    def build(self):
        with tools.chdir(f"requests-{self.version}"):
            self.run('python setup.py install --optimize=1 --prefix= --root="%s"' % self.package_folder)

