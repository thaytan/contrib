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
        tools.get("https://gitlab.gnome.org/GNOME/libxml2/-/archive/v{0}/libxml2-v{0}.tar.bz2".format(self.version))

    def build(self):
        args = ["--disable-static"]
        env = {"with_python_install_dir": os.path.join(self.package_folder, "lib", "python3.7", "site-packages")}
        with tools.chdir("%s-v%s" % (self.name, self.version)), tools.environment_append(env):
            self.run("sh autogen.sh")
            autotools = AutoToolsBuildEnvironment(self)
            autotools.configure(args=args)
            autotools.make()
            autotools.install()

    def package_info(self):
        self.env_info.PYTHONPATH = os.path.join(self.package_folder, "lib", "python3.7", "site-packages")
