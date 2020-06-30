import os

from conans import *


class PythonAppdirsConan(ConanFile):
    description = 'A small Python module for determining appropriate platform-specific dirs, e.g. a "user data dir".'
    license = "MIT"
    settings = {"os": ["Linux"], "arch": ["x86_64", "armv8"]}

    def build_requirements(self):
        self.build_requires("generators/1.0.0")
        self.build_requires("python-setuptools/[^41.2.0]")

    def requirements(self):
        self.requires("python/[^3.7.4]")

    def source(self):
        tools.get("https://pypi.io/packages/source/a/appdirs/appdirs-{0}.tar.gz".format(self.version))

    def build(self):
        with tools.chdir("appdirs-%s" % self.version):
            self.run('python setup.py install --optimize=1 --prefix= --root="%s"' % self.package_folder)
