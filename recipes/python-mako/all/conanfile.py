import os

from conans import *


class PythonMakoConan(ConanFile):
    description = "A super-fast templating language that borrows the best ideas from the existing templating languages"
    license = "Apache"
    settings = "build_type", "compiler", "arch_build", "os_build", "libc_build"

    def source(self):
        tools.get(f"https://github.com/sqlalchemy/mako/archive/rel_{self.version}.tar.gz".replace(".", "_"))

    build_requires = ("python-setuptools/[^41.2.0]",)
    requires = (
        "base/[^1.0.0]",
        "python/[^3.7.4]",
    )

    def build(self):
        with tools.chdir("mako-rel_" + self.version.replace(".", "_")):
            self.run('python setup.py install --optimize=1 --prefix= --root="%s"' % self.package_folder)
