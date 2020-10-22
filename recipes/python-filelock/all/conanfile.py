from conans import *


class PythonFilelockConan(ConanFile):
    description = "A platform independent file lock"
    license = "custom"
    settings = "build_type", "compiler", "arch_build", "os_build", "libc_build", "python"
    build_requires = ("python-setuptools/[^41.2.0]",)

    def requirements(self):
        self.requires(f"python/[~{self.settings.python}]")

    def source(self):
        tools.get(f"https://github.com/benediktschmitt/py-filelock/archive/v{self.version}.tar.gz")

    def build(self):
        self.run(f'python setup.py install --optimize=1 --prefix= --root="{self.package_folder}"', cwd=f"py-filelock-{self.version}")
