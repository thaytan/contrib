from conans import *


def conv_version(version):
    version = version.split(".")
    return version[0] + format(version[1], "0<3") + format(version[2], "0<3")


class SqliteConan(ConanFile):
    description = "A C library that implements an SQL database engine"
    license = "custom:Public Domain"
    settings = {"os": ["Linux"], "arch": ["x86_64", "armv8"]}
    build_requires = (
        "base/[^1.0.0]",
        "autotools/[^1.0.0]",
        "tcl/[^8.6.10]",
    )
    requires = (
        "base/[^1.0.0]",
        "zlib/[^1.2.11]",
        "readline/[^8.0]",
    )

    def source(self):
        tools.get(f"https://www.sqlite.org/2019/sqlite-src-{conv_version(self.version)}.zip")

    def build(self):
        autotools = AutoToolsBuildEnvironment(self)
        with tools.chdir(f"{self.name}-src-{conv_version(self.version)}"):
            self.run("chmod +x configure")
            autotools.configure()
            autotools.install()
