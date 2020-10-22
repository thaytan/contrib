from conans import *


class PythonPillowConan(ConanFile):
    description = "Python Image Library"
    license = "Python-Imaging-Library-License"
    settings = "build_type", "compiler", "arch_build", "os_build", "libc_build", "python"
    build_requires = (
        "cc/[^1.0.0]",
        "pkgconf/[^1.6.3]",
        "python-setuptools/[^41.2.0]",
        "zlib/[^1.2.11]",
        "libjpeg-turbo/[^2.0.4]",
    )

    def requirements(self):
        self.requires(f"python/[~{self.settings.python}]")

    def source(self):
        tools.get(f"https://github.com/python-pillow/Pillow/archive/{self.version}.tar.gz")

    def build(self):
        self.run(f'python setup.py install --optimize=1 --prefix= --root="{self.package_folder}"', f"Pillow-{self.version}")

