import os

from conans import ConanFile, tools


class PythonFilelockConan(ConanFile):
    description = "A platform independent file lock"
    license = "custom"
    settings = {"os": ["Linux"], "arch": ["x86_64", "armv8"]}

    def build_requirements(self):
        self.build_requires("generators/1.0.0")
        self.build_requires("python-setuptools/[^41.2.0]")

    def requirements(self):
        self.requires("python/[^3.7.4]")

    def source(self):
        tools.get("https://github.com/benediktschmitt/py-filelock/archive/v{0}.tar.gz".format(self.version))

    def build(self):
        with tools.chdir("py-filelock-{}".format(self.version)):
            self.run('python setup.py install --optimize=1 --prefix= --root="{}"'.format(self.package_folder))
