import os

from conans import ConanFile, Meson, tools


class PythonCairoConan(ConanFile):
    description = "Python bindings for the cairo graphics library"
    license = "LGPL"
    settings = {"os": ["Linux"], "arch": ["x86_64", "armv8"]}

    def build_requirements(self):
        self.build_requires("generators/1.0.0")
        self.build_requires("gcc/[^7.4.0]")
        self.build_requires("pkgconf/[^1.6.3]")

    def requirements(self):
        self.requires("python/[^3.7.4]")
        self.requires("cairo/[^1.16.0]")

    def source(self):
        tools.get("https://github.com/pygobject/pycairo/releases/download/v{0}/pycairo-{0}.tar.gz".format(self.version))

    def build(self):
        with tools.chdir("pycairo-%s" % self.version):
            self.run('python setup.py install --optimize=1 --prefix= --root="%s"' % self.package_folder)

    def package_info(self):
        self.env_info.PYTHONPATH.append(os.path.join(self.package_folder, "lib", "python3.7", "site-packages"))
