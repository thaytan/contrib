import os

from conans import *


class PythonPillowConan(ConanFile):
    description = "Python Image Library"
    license = "Python-Imaging-Library-License"
    settings = "build_type", "compiler", "arch_build", "os_build", "libc_build"
    build_requires = (
        "cc/[^1.0.0]",
        "pkgconf/[^1.6.3]",
        "python-setuptools/[^41.2.0]",
        "zlib/[^1.2.11]",
        "libjpeg-turbo/[^2.0.4]",
    )
    requires = (
        "base/[^1.0.0]",
        "python/[^3.7.4]",
    )

    def source(self):
        tools.get(f"https://github.com/python-pillow/Pillow/archive/{self.version}.tar.gz")

    def build(self):
        with tools.chdir(f"Pillow-{self.version}"):
            self.run('python setup.py install --optimize=1 --prefix= --root="%s"' % self.package_folder)

