from conans import *


class PythonRequestsConan(ConanFile):
    description = "Python Requests module"
    license = "Apache 2.0"
    settings = "build_type", "compiler", "arch_build", "os_build", "libc_build", "python"
    build_requires = (
        "cc/[^1.0.0]",
        "pkgconf/[^1.6.3]",
        "python-setuptools/[^41.2.0]",
    )

    def requirements(self):
        self.requires(f"python/[~{self.settings.python}]")

    def source(self):
        tools.get(f"https://github.com/psf/requests/archive/v{self.version}.tar.gz")

    def build(self):
        self.run(f'python setup.py install --optimize=1 --prefix= --root="{self.package_folder}"', cwd=f"requests-{self.version}")

