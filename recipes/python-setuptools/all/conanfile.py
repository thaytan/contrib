import os

from conans import *


class PythonSetuptoolsConan(ConanFile):
    description = "Easily download, build, install, upgrade, and uninstall Python packages"
    license = "Apache"
    settings = {"os": ["Linux"], "arch": ["x86_64", "armv8"]}
    requires = (
        "base/[^1.0.0]",
        "python/[^3.7.4]",
    )

    def source(self):
        tools.get(f"https://github.com/pypa/setuptools/archive/v{self.version}.tar.gz")

    def build(self):
        py_path = os.path.join(self.package_folder, "lib", "python3.7", "site-packages")
        env = {"PYTHONPATH": py_path}
        os.makedirs(py_path)
        with tools.chdir("setuptools-" + self.version), tools.environment_append(env):
            self.run("python bootstrap.py")
            self.run('python setup.py install --optimize=1 --prefix= --root="%s"' % self.package_folder)
