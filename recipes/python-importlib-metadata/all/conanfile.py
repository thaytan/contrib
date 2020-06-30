import os

from conans import *


class PythonImportlibMetadataConan(ConanFile):
    description = "Read metadata from Python packages"
    license = "Apache"
    settings = {"os": ["Linux"], "arch": ["x86_64", "armv8"]}
    build_requires = (
        "generators/1.0.0@",
        "python-setuptools/[^41.2.0]",
    )
    requires = ("python-zipp/[^3.1.0]",)

    def source(self):
        tools.get("https://gitlab.com/python-devs/importlib_metadata/-/archive/v{0}/importlib_metadata-v{0}.tar.bz2".format(self.version))

    def build(self):
        env = {
            "SETUPTOOLS_SCM_PRETEND_VERSION": self.version,
        }
        with tools.chdir("importlib_metadata-v{}".format(self.version)), tools.environment_append(env):
            self.run('python setup.py install --optimize=1 --prefix= --root="{}"'.format(self.package_folder))
