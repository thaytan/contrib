import os

from conans import *


class Libxml2Conan(ConanFile):
    description = "XML parsing library, version 2"
    license = "MIT"
    settings = "build_type", "compiler", "arch_build", "os_build", "libc_build"
    build_requires = (
        "cc/[^1.0.0]",
        "autotools/[^1.0.0]",
        "zlib/[^1.2.11]",
        "python/[^3.8.5]",
    )

    def source(self):
        tools.get(f"https://gitlab.gnome.org/GNOME/libxml2/-/archive/v{self.version}/libxml2-v{self.version}.tar.bz2")

    def build(self):
        args = [
            "--disable-shared",
        ]
        env = {"with_python_install_dir": os.path.join(self.package_folder, "lib", "python3.8", "site-packages")}
        with tools.chdir(f"{self.name}-v{self.version}"), tools.environment_append(env):
            self.run("sh autogen.sh")
            autotools = AutoToolsBuildEnvironment(self)
            autotools.configure(args=args)
            autotools.make()
            autotools.install()
