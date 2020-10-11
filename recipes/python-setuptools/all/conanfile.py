import os
from conans import *


class PythonSetuptoolsConan(ConanFile):
    description = "Easily download, build, install, upgrade, and uninstall Python packages"
    license = "Apache"
    settings = "build_type", "compiler", "arch_build", "os_build", "libc_build"
    requires = ("python/[^3.8.5]",)

    def source(self):
        tools.get(f"https://github.com/pypa/setuptools/archive/v{self.version}.tar.gz")

    def build(self):
        py_path = os.path.join(self.package_folder, "lib", "python3.8", "site-packages")
        env = {"PYTHONPATH": py_path}
        os.makedirs(py_path)
        with tools.chdir("setuptools-" + self.version), tools.environment_append(env):
            self.run("python bootstrap.py")
            self.run('python setup.py install --optimize=1 --prefix= --root="%s"' % self.package_folder)
