from build import *


class ElfutilsRecipe(Recipe):
    description = "Utilities and DSOs to handle ELF files and DWARF data"
    license = "LGPL3"
    exports = ("elfutils-clang.patch",)
    build_requires = (
        "cc/[^1.0.0]",
        "autotools/[^1.0.0]",
        "zlib/[^1.2.11]",
        "libarchive/[^3.4.3]",
    )

    def source(self):
        self.get(f"https://sourceware.org/elfutils/ftp/{self.version}/elfutils-{self.version}.tar.bz2")
        self.patch(f"elfutils-clang.patch")

    def build(self):
        args = [
            "--disable-debuginfod",
        ]
        os.environ["CFLAGS"] += " -Wno-error"
        os.environ["CXXFLAGS"] += " -Wno-error"
        self.autotools(args)
