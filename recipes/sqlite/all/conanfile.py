from conans import *


def conv_version(version):
    version = version.split(".")
    return version[0] + format(version[1], "0<3") + format(version[2], "0<3")


class SqliteConan(ConanFile):
    description = "A C library that implements an SQL database engine"
    license = "custom"
    settings = "build_type", "compiler", "arch_build", "os_build", "libc_build"
    build_requires = (
        "bootstrap-llvm/[^10.0.1]",
        "make/[^4.3]",
        "tcl/[^8.6.10]",
        "zlib/[^1.2.11]",
        "readline/[^8.0]",
    )

    def source(self):
        tools.get(f"https://www.sqlite.org/2019/sqlite-src-{conv_version(self.version)}.zip")

    def build(self):
        args = [
            "--disable-shared",
        ]
        autotools = AutoToolsBuildEnvironment(self)
        with tools.chdir(f"{self.name}-src-{conv_version(self.version)}"):
            self.run("chmod +x configure")
            autotools.configure(args=args)
            autotools.install()
