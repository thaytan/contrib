from conans import *


class PythonMakoConan(ConanFile):
    description = "A super-fast templating language that borrows the best ideas from the existing templating languages"
    license = "Apache"
    settings = "build_type", "compiler", "arch_build", "os_build", "libc_build"
    build_requires = ("python-setuptools/[^50.3.0]",)
    requires = ("python/[^3.8.5]",)

    def source(self):
        tools.get(f"https://github.com/sqlalchemy/mako/archive/rel_{self.version.replace('.', '_')}.tar.gz")

    def build(self):
        self.run(f'python setup.py install --optimize=1 --prefix= --root="{self.package_folder}"', cwd=f"mako-rel_{self.version.replace('.', '_')}")
