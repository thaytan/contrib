import os

from conans import ConanFile, Meson, tools


class PythonPillowConan(ConanFile):
    description = "Python Image Library"
    license = "Python-Imaging-Library-License"
    settings = {"os": ["Linux"], "arch": ["x86_64", "armv8"]}

    def build_requirements(self):
        self.build_requires("generators/1.0.0")
        self.build_requires("gcc/[^7.4.0]")
        self.build_requires("pkgconf/[^1.6.3]")
        self.build_requires("python-setuptools/[^41.2.0]")
        self.build_requires("zlib/[^1.2.11]")
        self.build_requires("libjpeg-turbo/[^2.0.4]")

    def requirements(self):
        self.requires("python/[^3.7.4]")

    def source(self):
        tools.get("https://github.com/python-pillow/Pillow/archive/{0}.tar.gz".format(self.version))

    def build(self):
        with tools.chdir("Pillow-{0}".format(self.version)):
            self.run('python setup.py install --optimize=1 --prefix= --root="%s"' % self.package_folder)

