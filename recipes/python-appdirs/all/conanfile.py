import os

from conans import ConanFile, tools

class PythonAppdirsConan(ConanFile):
    name = "python-appdirs"
    version = tools.get_env("GIT_TAG", "1.4.4")
    description = "A small Python module for determining appropriate platform-specific dirs, e.g. a \"user data dir\"."
    license = "MIT"
    settings = "os", "arch", "compiler", "build_type"

    def build_requirements(self):
        self.build_requires("generators/1.0.0@%s/stable" % self.user)
        self.build_requires("python-setuptools/[>=41.2.0]@%s/stable" % self.user)

    def requirements(self):
        self.requires("python/[>=3.7.4]@%s/stable" % self.user)

    def source(self):
        tools.get("https://pypi.io/packages/source/a/appdirs/appdirs-{0}.tar.gz".format(self.version))

    def build(self):
        with tools.chdir("appdirs-%s" % self.version):
            self.run('python setup.py install --optimize=1 --prefix= --root="%s"' % self.package_folder)
