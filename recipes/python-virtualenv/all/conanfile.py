import os

from conans import *


class PythonVirtualenvConan(ConanFile):
    description = "Virtual Python Environment builder"
    license = "MIT"
    settings = "build_type", "compiler", "arch_build", "os_build", "libc_build"
    requires = (
        "base/[^1.0.0]",
        "python/[^3.7.4]",
        "python-setuptools/[^41.2.0]",
        "python-appdirs/[^1.4.4]",
        "python-distlib/[^0.3.0]",
        "python-filelock/[^3.0.12]",
        "python-six/[^1.15.0]",
        "python-importlib-metadata/[^1.6.0]",
    )

    def source(self):
        tools.get(f"https://github.com/pypa/virtualenv/archive/{self.version}.tar.gz")

    def build(self):
        env = {
            "SETUPTOOLS_SCM_PRETEND_VERSION": self.version,
        }
        with tools.chdir(f"virtualenv-{self.version}"), tools.environment_append(env):
            self.run('python setup.py install --optimize=1 --prefix= --root="%s"' % self.package_folder)

