import os

from conans import *


class Libxml2Conan(ConanFile):
    description = "XML parsing library, version 2"
    license = "MIT"
    settings = {"os": ["Linux"], "arch": ["x86_64", "armv8"]}
    build_requires = (
        "generators/1.0.0",
        "autotools/[^1.0.0]",
        "zlib/[^1.2.11]",
        "python/[^3.7.4]",
    )

    def source(self):
        tools.get(f"https://gitlab.gnome.org/GNOME/libxml2/-/archive/v{self.version}/libxml2-v{self.version}.tar.bz2")

    def build(self):
        args = ["--disable-static"]
        env = {"with_python_install_dir": os.path.join(self.package_folder, "lib", "python3.7", "site-packages")}
        with tools.chdir(f"{self.name}-v{self.version}"), tools.environment_append(env):
            self.run("sh autogen.sh")
            autotools = AutoToolsBuildEnvironment(self)
            autotools.configure(args=args)
            autotools.make()
            autotools.install()

    def package_info(self):
        self.env_info.PYTHONPATH = os.path.join(self.package_folder, "lib", "python3.7", "site-packages")
