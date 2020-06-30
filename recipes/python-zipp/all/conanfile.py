import os

from conans import ConanFile, tools

class PythonZippConan(ConanFile):
    name = "python-zipp"
    description = "Pathlib-compatible object wrapper for zip files"
    license = "MIT"
    settings = "os", "arch", "compiler", "build_type"

    def build_requirements(self):
        self.build_requires("generators/1.0.0@{}/stable".format(self.user))
        self.build_requires("python-setuptools/[>=41.2.0]@%s/stable" % self.user)

    def requirements(self):
        self.requires("python/[>=3.7.4]@{}/stable".format(self.user))

    def source(self):
        tools.get("https://github.com/jaraco/zipp/archive/v{0}.tar.gz".format(self.version))

    def build(self):
        with tools.chdir("zipp-{}".format(self.version)):
            self.run('python setup.py install --optimize=1 --prefix= --root="{}"'.format(self.package_folder))
