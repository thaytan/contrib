import os

from conans import *


class PythonRequestsConan(ConanFile):
    description = "Python Requests module"
    license = "Apache 2.0"
    settings = {"os": ["Linux"], "arch": ["x86_64", "armv8"]}

    def build_requirements(self):
        self.build_requires("generators/1.0.0")
        self.build_requires("gcc/[^7.4.0]")
        self.build_requires("pkgconf/[^1.6.3]")
        self.build_requires("python-setuptools/[^41.2.0]")

    def requirements(self):
        self.requires("python/[^3.7.4]")

    def source(self):
        tools.get("https://github.com/psf/requests/archive/v{0}.tar.gz".format(self.version))

    def build(self):
        with tools.chdir("requests-{0}".format(self.version)):
            self.run('python setup.py install --optimize=1 --prefix= --root="%s"' % self.package_folder)

