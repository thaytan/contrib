from conans import *


class PythonAppdirsConan(ConanFile):
    description = 'A small Python module for determining appropriate platform-specific dirs, e.g. a "user data dir".'
    license = "MIT"
    settings = "build_type", "compiler", "arch_build", "os_build", "libc_build", "python"
    build_requires = ("python-setuptools/[^41.2.0]",)

    def requirements(self):
        self.requires(f"python/[~{self.settings.python}]")

    def source(self):
        tools.get(f"https://pypi.io/packages/source/a/appdirs/appdirs-{self.version}.tar.gz")

    def build(self):
        self.run(f'python setup.py install --optimize=1 --prefix= --root="{self.package_folder}"', cwd=f"appdirs-{self.version}")
