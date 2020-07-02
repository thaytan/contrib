import os

from conans import *


class PythonCairoConan(ConanFile):
    description = "Python bindings for the cairo graphics library"
    license = "LGPL"
    settings = {"os": ["Linux"], "arch": ["x86_64", "armv8"]}
    build_requires = (
        "gcc/[^7.4.0]",
        "pkgconf/[^1.6.3]",
    )
    requires = (
        "generators/[^1.0.0]",
        "python/[^3.7.4]",
        "cairo/[^1.16.0]",
    )

    def source(self):
        tools.get(f"https://github.com/pygobject/pycairo/releases/download/v{self.version}/pycairo-{self.version}.tar.gz")

    def build(self):
        with tools.chdir(f"pycairo-{self.version}"):
            self.run('python setup.py install --optimize=1 --prefix= --root="%s"' % self.package_folder)

    def package_info(self):
        self.env_info.PYTHONPATH.append(os.path.join(self.package_folder, "lib", "python3.7", "site-packages"))
