from conans import *


class PythonDistlibConan(ConanFile):
    name = "python-distlib"
    description = "Low-level components of distutils2/packaging"
    license = "PSF"
    settings = {"os_build": ["Linux"], "arch_build": ["x86_64", "armv8"]}
        requires = (
        "base/[^1.0.0]",
        "python/[^3.7.4]",
    )

    def source(self):
        tools.get(f"https://files.pythonhosted.org/packages/source/d/distlib/distlib-{self.version}.zip")

    def build(self):
        with tools.chdir(f"distlib-{self.version}"):
            self.run(f'python setup.py install --optimize=1 --prefix= --root="{self.package_folder}"')
