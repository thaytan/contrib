from conans import *


class PythonDistlibConan(ConanFile):
    description = "Low-level components of distutils2/packaging"
    license = "PSF"
    settings = "build_type", "compiler", "arch_build", "os_build", "libc_build"

    def requirements(self):
        self.requires(f"python/[~{self.settings.python}]")

    def source(self):
        tools.get(f"https://files.pythonhosted.org/packages/source/d/distlib/distlib-{self.version}.zip")

    def build(self):
        self.run(f'python setup.py install --optimize=1 --prefix= --root="{self.package_folder}"', cwd=f"distlib-{self.version}")
