from build import *


def conv_version(version):
    version = version.split(".")
    return version[0] + format(version[1], "0<3") + format(version[2], "0<3")


class Sqlite(Recipe):
    description = "A C library that implements an SQL database engine"
    license = "custom"
    build_requires = (
        "cc/[^1.0.0]",
        "make/[^4.3]",
        "tcl/[^8.6.10]",
    )
    requires = (
        "zlib/[^1.2.11]",
        "readline/[^8.0]",
    )

    def source(self):
        self.get(f"https://www.sqlite.org/2019/sqlite-src-{conv_version(self.version)}.zip")

    def build(self):
        self.exe("chmod +x configure")

        self.autotools()
