import os

from conans import ConanFile, tools


class PythonSixConan(ConanFile):
    description = "Python 2 and 3 compatibility utilities"
    license = "MIT"
    settings = {"os": ["Linux"], "arch": ["x86_64", "armv8"]}

    def build_requirements(self):
        self.build_requires("generators/1.0.0")
        self.build_requires("autotools/1.0.0")
        self.build_requires("python-setuptools/[^41.2.0]")

    def source(self):
        tools.get("https://pypi.io/packages/source/s/six/six-{0}.tar.gz".format(self.version))

    def build(self):
        with tools.chdir("six-{}".format(self.version)):
            self.run('python setup.py install --optimize=1 --prefix= --root="%s"' % self.package_folder)
