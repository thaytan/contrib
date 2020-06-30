import os

from conans import ConanFile, Meson, tools

class PythonRequestsConan(ConanFile):
    name = "python-requests"
    description = "Python Requests module"
    license = "Apache 2.0"
    settings = "os", "arch", "compiler", "build_type"

    def build_requirements(self):
        self.build_requires("generators/1.0.0@%s/stable" % self.user)
        self.build_requires("gcc/[>=7.4.0]@%s/stable" % self.user)
        self.build_requires("pkgconf/[>=1.6.3]@%s/stable" % self.user)
        self.build_requires("python-setuptools/[>=41.2.0]@%s/stable" % self.user)

    def requirements(self):
        self.requires("python/[>=3.7.4]@%s/stable" % self.user)

    def source(self):
        tools.get("https://github.com/psf/requests/archive/v{0}.tar.gz".format(self.version))

    def build(self):
        with tools.chdir("requests-{0}".format(self.version)):
            self.run('python setup.py install --optimize=1 --prefix= --root="%s"' % self.package_folder)