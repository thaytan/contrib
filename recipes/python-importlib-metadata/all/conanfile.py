import os

from conans import *


class PythonImportlibMetadataConan(ConanFile):
    description = "Read metadata from Python packages"
    license = "Apache"
    settings = "build_type", "compiler", "arch_build", "os_build", "libc_build"
    build_requires = ("python-setuptools/[^41.2.0]",)
    requires = (
        "base/[^1.0.0]",
        "python-zipp/[^3.1.0]",
    )

    def source(self):
        tools.get(f"https://gitlab.com/python-devs/importlib_metadata/-/archive/v{self.version}/importlib_metadata-v{self.version}.tar.bz2")

    def build(self):
        env = {
            "SETUPTOOLS_SCM_PRETEND_VERSION": self.version,
        }
        with tools.chdir(f"importlib_metadata-v{self.version}"), tools.environment_append(env):
            self.run(f'python setup.py install --optimize=1 --prefix= --root="{self.package_folder}"')
