import os

from conans import *


class Libxml2Conan(ConanFile):
    description = "XML parsing library, version 2"
    license = "MIT"
    settings = "build_type", "compiler", "arch_build", "os_build", "libc_build", "python"
    build_requires = (
        "autotools/[^1.0.0]",
        "zlib/[^1.2.11]",
    )

    def build_requirements(self):
        self.build_requires(f"python/[~{self.settings.python}]")

    def source(self):
        tools.get(f"https://gitlab.gnome.org/GNOME/libxml2/-/archive/v{self.version}/libxml2-v{self.version}.tar.bz2")

    def build(self):
        args = [
            "--disable-static",
        ]
        env = {
            "with_python_install_dir": os.path.join(self.package_folder, "lib", f"python{self.settings.python}", "site-packages"),
            "NOCONFIGURE": "1",
        }
        with tools.environment_append(env):
            self.run("sh autogen.sh", cwd=f"libxml2-v{self.version}")
            autotools = AutoToolsBuildEnvironment(self)
            autotools.configure(f"libxml2-v{self.version}", args=args)
            autotools.make()
            autotools.install()
