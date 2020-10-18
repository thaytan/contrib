import os
from conans import *


class MesonConan(ConanFile):
    description = "High productivity build system"
    license = "Apache"
    settings = "build_type", "compiler", "arch_build", "os_build", "libc_build"
    requires = (
        "python-setuptools/[^50.3.0]",
        "ninja/[^1.9.0]",
        "pkgconf/[^1.7.3]",
    )

    def source(self):
        tools.get(f"https://github.com/mesonbuild/meson/releases/download/{self.version}/meson-{self.version}.tar.gz")

    def build(self):
        py_path = os.path.join(self.package_folder, "lib", "python3.8", "site-packages")
        env = {"PYTHONPATH": os.environ["PYTHONPATH"] + os.pathsep + py_path}
        os.makedirs(py_path)
        with tools.environment_append(env):
            self.run(f'python setup.py install --optimize=1 --prefix= --root="{self.package_folder}"', cwd=f"meson-{self.version}")
