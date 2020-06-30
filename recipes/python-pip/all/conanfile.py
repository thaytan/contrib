import os

from conans import *


class PythonPipConan(ConanFile):
    description = "High productivity build system"
    license = "MIT"
    settings = {"os": ["Linux"], "arch": ["x86_64", "armv8"]}

    def source(self):
        tools.get("https://github.com/pypa/pip/archive/%s.tar.gz" % self.version)

    build_requires = (
        "generators/1.0.0",
        "python-setuptools/[^41.2.0]",
    )
    requires = ("python/[^3.7.4]",)

    def build(self):
        with tools.chdir("pip-" + self.version):
            self.run('python setup.py install --optimize=1 --prefix= --root="%s"' % self.package_folder)

    def package_info(self):
        self.env_info.PYTHONPATH.append(os.path.join(self.package_folder, "lib", "python3.7", "site-packages"))
