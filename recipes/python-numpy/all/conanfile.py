from conans import *


class PythonNumpyConan(ConanFile):
    description = "conan package for Python Numpy module"
    license = "BSD"
    settings = "build_type", "compiler", "arch_build", "os_build", "libc_build", "python"
    build_requires = (
        "cc/[^1.0.0]",
        "pkgconf/[^1.6.3]",
        "python-setuptools/[^41.2.0]",
        "cython/[^0.29.19]",
    )

    def requirements(self):
        self.requires(f"python/[~{self.settings.python}]")

    def source(self):
        tools.get(f"https://github.com/numpy/numpy/releases/download/v{self.version}/numpy-{self.version}.tar.gz")

    def build(self):
        self.run(f'python setup.py install --optimize=1 --prefix= --root="{self.package_folder}"', cwd=f"numpy-{self.version}")

